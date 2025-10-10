using Microsoft.Extensions.DependencyInjection;

namespace TaskService.Infrastructure;

public static class IServiceCollectionExtension
{
  public static IServiceCollection RegisterServices(this IServiceCollection services)
  {
    return services;
  }
}