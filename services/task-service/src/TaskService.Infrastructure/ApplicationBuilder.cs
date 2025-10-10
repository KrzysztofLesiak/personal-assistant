
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;

namespace TaskService.Infrastructure;

public static class ApplicationBuilder
{
    public static WebApplication BuildApplication()
    {
        var builder = WebApplication.CreateBuilder();

        builder.Services.AddControllers();

        builder.Services.AddEndpointsApiExplorer();
        builder.Services.AddSwaggerGen();

        return;
    }

}
