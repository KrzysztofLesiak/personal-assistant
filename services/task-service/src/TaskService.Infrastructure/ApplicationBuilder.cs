
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;

namespace TaskService.Infrastructure;

public static class ApplicationBuilder
{
    public static WebApplication BuildApplication()
    {
        var builder = WebApplication.CreateBuilder();

        // Register only foundational services here; keep API-specific middleware in the API project
        builder.Services.AddControllers();

        return builder.Build();
    }

}
