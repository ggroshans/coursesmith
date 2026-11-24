---
title: Dependency injection
ms.date: 01/26/2026
---

# .NET dependency injection

.NET supports the *dependency injection* (DI) pattern. Dependency injection in .NET is built into the framework. See the [options pattern](../options.md) and <xref:Microsoft.Extensions.Options.IOptions`1>.

> [!IMPORTANT]
> The examples use the `Microsoft.NET.Sdk.Worker` SDK.

:::code language="csharp" source="snippets/Program.cs" id="All":::

[!INCLUDE [prereqs](../includes/prereqs.md)]

:::zone pivot="cs1"

Register the service with <xref:System.IServiceProvider.GetService*> or <xref:System.Collections.Generic.List`1.Add*?displayProperty=nameWithType>. A [typed link](xref:System.String) reads as text.

:::zone-end

#### [Windows](#tab/windows)

Edit the .config file, then build the .dll.

---

## Lifetimes {#lifetimes}

A transient service is created each time it is requested.

## Next steps

- [Service lifetimes](service-lifetimes.md)

## Last words

The end of the page.
