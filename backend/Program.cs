using System.Collections.Concurrent;
using System.Globalization;
using System.Net;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using CsvHelper;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Server.Kestrel.Core;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = WebApplication.CreateBuilder(args);

builder.Services.Configure<IISServerOptions>(options =>
{
    options.MaxRequestBodySize = 100 * 1024 * 1024; // 100MB
});

builder.Services.Configure<KestrelServerOptions>(options =>
{
    options.Limits.MaxRequestBodySize = 100 * 1024 * 1024; // 100MB
});

builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
        policy.WithOrigins("http://localhost:4200", "http://localhost:3000")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials());
});

builder.Services.AddSingleton<UploadedFilesStore>();
builder.Services.AddSingleton<TrainingStateStore>();
builder.Services.AddSingleton<SimulationStateStore>();
builder.Services.AddSingleton<WebSocketConnectionManager>();
builder.Services.AddHostedService<SimulationBroadcastService>();

var app = builder.Build();

app.UseCors();
app.UseWebSockets();

app.MapGet("/", () => Results.Json(new Dictionary<string, object>
{
    ["message"] = "Welcome to MiniML - Predictive Quality Control Backend API"
}));

app.MapGet("/health", () => Results.Json(new Dictionary<string, object>
{
    ["status"] = "healthy",
    ["service"] = "miniml-backend"
}));

// Upload endpoints
app.MapPost("/upload", async (HttpRequest request, UploadedFilesStore store) =>
{
    if (!request.HasFormContentType)
    {
        return Results.Json(new { detail = "Invalid form data" }, statusCode: StatusCodes.Status400BadRequest);
    }

    var form = await request.ReadFormAsync();
    var file = form.Files.GetFile("file");
    if (file == null)
    {
        return Results.Json(new { detail = "File is required" }, statusCode: StatusCodes.Status400BadRequest);
    }

    if (!file.FileName.EndsWith(".csv", StringComparison.OrdinalIgnoreCase))
    {
        return Results.Json(new { detail = "Only CSV files are allowed" }, statusCode: StatusCodes.Status400BadRequest);
    }

    try
    {
        using var ms = new MemoryStream();
        await file.CopyToAsync(ms);
        var contentBytes = ms.ToArray();
        var contentText = Encoding.UTF8.GetString(contentBytes);

        // Parse CSV to compute stats
        int rows = 0;
        int columns = 0;
        long missingValuesCount = 0;
        using (var reader = new StringReader(contentText))
        using (var csv = new CsvReader(reader, CultureInfo.InvariantCulture))
        {
            // Read header
            if (await csv.ReadAsync())
            {
                csv.ReadHeader();
                columns = csv.HeaderRecord?.Length ?? 0;
            }

            while (await csv.ReadAsync())
            {
                rows++;
                for (int i = 0; i < columns; i++)
                {
                    var value = csv.GetField(i);
                    if (string.IsNullOrWhiteSpace(value))
                    {
                        missingValuesCount++;
                    }
                }
            }
        }

        double denominator = Math.Max(1, (double)rows * Math.Max(1, columns));
        double missingPercentage = (missingValuesCount / denominator) * 100.0;

        var fileInfo = new UploadedFileInfo
        {
            FileName = file.FileName,
            FileSize = contentBytes.LongLength,
            Rows = rows,
            Columns = columns,
            MissingPercentage = missingPercentage,
            UploadTimeIso = DateTime.UtcNow.ToString("o"),
            Content = contentBytes
        };

        store.Save(fileInfo);

        return Results.Json(new Dictionary<string, object>
        {
            ["success"] = true,
            ["message"] = "File uploaded successfully",
            ["data"] = new Dictionary<string, object>
            {
                ["filename"] = fileInfo.FileName,
                ["file_size"] = fileInfo.FileSize,
                ["rows"] = fileInfo.Rows,
                ["columns"] = fileInfo.Columns,
                ["missing_values"] = missingPercentage.ToString("0.00") + "%",
                ["upload_time"] = fileInfo.UploadTimeIso
            }
        });
    }
    catch (Exception ex)
    {
        return Results.Json(new { detail = $"Error processing file: {ex.Message}" }, statusCode: StatusCodes.Status500InternalServerError);
    }
});

app.MapGet("/files", (UploadedFilesStore store) =>
{
    var files = store.GetAll().Select(info => new Dictionary<string, object>
    {
        ["filename"] = info.FileName,
        ["file_size"] = info.FileSize,
        ["rows"] = info.Rows,
        ["columns"] = info.Columns,
        ["missing_values"] = info.MissingPercentage.ToString("0.00") + "%",
        ["upload_time"] = info.UploadTimeIso
    }).ToList();

    return Results.Json(new Dictionary<string, object>
    {
        ["files"] = files
    });
});

app.MapDelete("/files/{filename}", (string filename, UploadedFilesStore store) =>
{
    if (store.Delete(filename))
    {
        return Results.Json(new Dictionary<string, object>
        {
            ["success"] = true,
            ["message"] = $"File {filename} deleted successfully"
        });
    }
    return Results.Json(new { detail = "File not found" }, statusCode: StatusCodes.Status404NotFound);
});

// Training endpoints
app.MapPost("/date-ranges", async (HttpRequest req, TrainingStateStore store) =>
{
    try
    {
        var payload = await JsonSerializer.DeserializeAsync<DateRangesRequest>(req.Body, new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        });
        if (payload == null)
        {
            return Results.Json(new { detail = "Invalid payload" }, statusCode: StatusCodes.Status400BadRequest);
        }

        store.DateRanges = new Dictionary<string, object?>
        {
            ["training"] = payload.Training,
            ["testing"] = payload.Testing,
            ["simulation"] = payload.Simulation,
            ["saved_at"] = DateTime.UtcNow.ToString("o")
        };

        return Results.Json(new Dictionary<string, object>
        {
            ["success"] = true,
            ["message"] = "Date ranges saved successfully",
            ["data"] = store.DateRanges
        });
    }
    catch (Exception ex)
    {
        return Results.Json(new { detail = $"Error saving date ranges: {ex.Message}" }, statusCode: StatusCodes.Status500InternalServerError);
    }
});

app.MapGet("/date-ranges", (TrainingStateStore store) => Results.Json(new Dictionary<string, object>
{
    ["success"] = true,
    ["data"] = store.DateRanges
}));

app.MapPost("/training-complete", async (HttpRequest req, TrainingStateStore store) =>
{
    try
    {
        var payload = await JsonSerializer.DeserializeAsync<TrainingCompleteRequest>(req.Body, new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        });
        if (payload == null)
        {
            return Results.Json(new { detail = "Invalid payload" }, statusCode: StatusCodes.Status400BadRequest);
        }

        store.State.IsTraining = false;
        store.State.Progress = 100;
        store.State.Metrics = payload.Metrics;
        store.State.TrainingData = payload.TrainingData ?? new List<Dictionary<string, object?>>();
        store.State.CompletedAtIso = DateTime.UtcNow.ToString("o");

        return Results.Json(new Dictionary<string, object>
        {
            ["success"] = true,
            ["message"] = "Training completed successfully",
            ["data"] = new Dictionary<string, object?>
            {
                ["metrics"] = payload.Metrics,
                ["training_data"] = store.State.TrainingData
            }
        });
    }
    catch (Exception ex)
    {
        return Results.Json(new { detail = $"Error processing training completion: {ex.Message}" }, statusCode: StatusCodes.Status500InternalServerError);
    }
});

app.MapGet("/training-status", (TrainingStateStore store) => Results.Json(new Dictionary<string, object>
{
    ["success"] = true,
    ["data"] = store.State.ToDictionary()
}));

app.MapPost("/start-training", (TrainingStateStore store) =>
{
    store.State.IsTraining = true;
    store.State.Progress = 0;
    store.State.StartedAtIso = DateTime.UtcNow.ToString("o");
    return Results.Json(new Dictionary<string, object>
    {
        ["success"] = true,
        ["message"] = "Training started successfully"
    });
});

app.MapPost("/stop-training", (TrainingStateStore store) =>
{
    store.State.IsTraining = false;
    store.State.StoppedAtIso = DateTime.UtcNow.ToString("o");
    return Results.Json(new Dictionary<string, object>
    {
        ["success"] = true,
        ["message"] = "Training stopped successfully"
    });
});

// Simulation endpoints
app.MapPost("/simulation/start", (SimulationStateStore store) =>
{
    store.State.IsRunning = true;
    store.State.StartedAtIso = DateTime.UtcNow.ToString("o");
    store.State.Predictions.Clear();
    store.State.Stats = new SimulationStats();
    return Results.Json(new Dictionary<string, object>
    {
        ["success"] = true,
        ["message"] = "Simulation started successfully"
    });
});

app.MapPost("/simulation/stop", (SimulationStateStore store) =>
{
    store.State.IsRunning = false;
    store.State.StoppedAtIso = DateTime.UtcNow.ToString("o");
    return Results.Json(new Dictionary<string, object>
    {
        ["success"] = true,
        ["message"] = "Simulation stopped successfully"
    });
});

app.MapGet("/simulation/status", (SimulationStateStore store) => Results.Json(new Dictionary<string, object>
{
    ["success"] = true,
    ["data"] = store.State.ToDictionary()
}));

app.MapGet("/simulation/predictions", (SimulationStateStore store) => Results.Json(new Dictionary<string, object>
{
    ["success"] = true,
    ["data"] = new Dictionary<string, object>
    {
        ["predictions"] = store.State.Predictions,
        ["stats"] = store.State.Stats.ToDictionary()
    }
}));

app.Map("/ws/simulation", async (HttpContext context, WebSocketConnectionManager manager) =>
{
    if (!context.WebSockets.IsWebSocketRequest)
    {
        context.Response.StatusCode = (int)HttpStatusCode.BadRequest;
        return;
    }

    using var socket = await context.WebSockets.AcceptWebSocketAsync();
    var id = manager.Add(socket);
    try
    {
        // Keep the socket open until client closes
        var buffer = new byte[4];
        while (socket.State == WebSocketState.Open)
        {
            var result = await socket.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);
            if (result.MessageType == WebSocketMessageType.Close)
            {
                break;
            }
        }
    }
    finally
    {
        manager.Remove(id);
        if (socket.State == WebSocketState.Open)
        {
            await socket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", CancellationToken.None);
        }
    }
});

app.Run("http://0.0.0.0:8000");

// Stores and models
public sealed class UploadedFilesStore
{
    private readonly ConcurrentDictionary<string, UploadedFileInfo> fileNameToInfo = new();

    public void Save(UploadedFileInfo info) => fileNameToInfo[info.FileName] = info;

    public IReadOnlyCollection<UploadedFileInfo> GetAll() => fileNameToInfo.Values.ToList();

    public bool Delete(string filename) => fileNameToInfo.TryRemove(filename, out _);
}

public sealed class UploadedFileInfo
{
    public string FileName { get; set; } = string.Empty;
    public long FileSize { get; set; }
    public int Rows { get; set; }
    public int Columns { get; set; }
    public double MissingPercentage { get; set; }
    public string UploadTimeIso { get; set; } = string.Empty;
    public byte[] Content { get; set; } = Array.Empty<byte>();
}

public sealed class TrainingStateStore
{
    public Dictionary<string, object?> DateRanges { get; set; } = new();
    public TrainingState State { get; } = new();
}

public sealed class TrainingState
{
    public bool IsTraining { get; set; }
    public int Progress { get; set; }
    public Dictionary<string, double>? Metrics { get; set; }
    public List<Dictionary<string, object?>> TrainingData { get; set; } = new();
    public string? StartedAtIso { get; set; }
    public string? CompletedAtIso { get; set; }
    public string? StoppedAtIso { get; set; }

    public Dictionary<string, object?> ToDictionary() => new()
    {
        ["is_training"] = IsTraining,
        ["progress"] = Progress,
        ["metrics"] = Metrics,
        ["training_data"] = TrainingData,
        ["started_at"] = StartedAtIso,
        ["completed_at"] = CompletedAtIso,
        ["stopped_at"] = StoppedAtIso
    };
}

public sealed class DateRangesRequest
{
    public Dictionary<string, object?> Training { get; set; } = new();
    public Dictionary<string, object?> Testing { get; set; } = new();
    public Dictionary<string, object?> Simulation { get; set; } = new();
}

public sealed class TrainingCompleteRequest
{
    public Dictionary<string, double>? Metrics { get; set; }
    public List<Dictionary<string, object?>>? TrainingData { get; set; }
}

public sealed class SimulationStateStore
{
    public SimulationState State { get; } = new();
}

public sealed class SimulationState
{
    public bool IsRunning { get; set; }
    public string? StartedAtIso { get; set; }
    public string? StoppedAtIso { get; set; }
    public List<Dictionary<string, object?>> Predictions { get; } = new();
    public SimulationStats Stats { get; set; } = new();

    public Dictionary<string, object?> ToDictionary() => new()
    {
        ["is_running"] = IsRunning,
        ["predictions"] = Predictions,
        ["stats"] = Stats.ToDictionary(),
        ["started_at"] = StartedAtIso,
        ["stopped_at"] = StoppedAtIso
    };
}

public sealed class SimulationStats
{
    public int TotalPredictions { get; set; }
    public int OutOfRange { get; set; }
    public int Accuracy { get; set; }

    public Dictionary<string, object> ToDictionary() => new()
    {
        ["total_predictions"] = TotalPredictions,
        ["out_of_range"] = OutOfRange,
        ["accuracy"] = Accuracy
    };
}

public sealed class WebSocketConnectionManager
{
    private readonly ConcurrentDictionary<Guid, WebSocket> connections = new();

    public Guid Add(WebSocket socket)
    {
        var id = Guid.NewGuid();
        connections[id] = socket;
        return id;
    }

    public void Remove(Guid id)
    {
        connections.TryRemove(id, out _);
    }

    public async Task BroadcastAsync(string message, CancellationToken cancellationToken)
    {
        var bytes = Encoding.UTF8.GetBytes(message);
        var segment = new ArraySegment<byte>(bytes);
        var toRemove = new List<Guid>();

        foreach (var kvp in connections)
        {
            var socket = kvp.Value;
            if (socket.State != WebSocketState.Open)
            {
                toRemove.Add(kvp.Key);
                continue;
            }

            try
            {
                await socket.SendAsync(segment, WebSocketMessageType.Text, true, cancellationToken);
            }
            catch
            {
                toRemove.Add(kvp.Key);
            }
        }

        foreach (var id in toRemove)
        {
            Remove(id);
        }
    }
}

public sealed class SimulationBroadcastService : BackgroundService
{
    private readonly SimulationStateStore store;
    private readonly WebSocketConnectionManager manager;

    public SimulationBroadcastService(SimulationStateStore store, WebSocketConnectionManager manager)
    {
        this.store = store;
        this.manager = manager;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var random = new Random();
        while (!stoppingToken.IsCancellationRequested)
        {
            await Task.Delay(TimeSpan.FromSeconds(2), stoppingToken);

            Dictionary<string, object?> message;
            if (store.State.IsRunning)
            {
                var prediction = GeneratePrediction(random);
                store.State.Predictions.Add(prediction);
                store.State.Stats.TotalPredictions++;
                if (Convert.ToString(prediction["prediction"]) == "Fail")
                {
                    store.State.Stats.OutOfRange++;
                }

                int correctCount = store.State.Predictions.Count(p => Convert.ToBoolean(p["correct"]) == true);
                store.State.Stats.Accuracy = store.State.Predictions.Count == 0 ? 0 : (int)Math.Round((double)correctCount / store.State.Predictions.Count * 100.0);

                message = new Dictionary<string, object?>
                {
                    ["type"] = "prediction",
                    ["data"] = prediction,
                    ["stats"] = store.State.Stats.ToDictionary()
                };
            }
            else
            {
                message = new Dictionary<string, object?>
                {
                    ["type"] = "status",
                    ["data"] = store.State.ToDictionary()
                };
            }

            var json = JsonSerializer.Serialize(message);
            await manager.BroadcastAsync(json, stoppingToken);
        }
    }

    private static Dictionary<string, object?> GeneratePrediction(Random random)
    {
        var now = DateTime.Now;
        var sampleId = $"SAMPLE-{random.Next(100, 999)}";
        var isPass = random.NextDouble() > 0.2;
        var prediction = isPass ? "Pass" : "Fail";
        var confidence = random.Next(80, 101);
        var computationTime = random.Next(50, 151);
        var threshold = 85;
        var correct = random.NextDouble() > 0.1;

        return new Dictionary<string, object?>
        {
            ["time"] = now.ToString("h:mm tt", CultureInfo.InvariantCulture),
            ["sample_id"] = sampleId,
            ["prediction"] = prediction,
            ["confidence"] = confidence,
            ["computation_time"] = computationTime,
            ["threshold"] = threshold,
            ["correct"] = correct
        };
    }
}


