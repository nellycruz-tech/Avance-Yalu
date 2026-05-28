# ============================================================
#  fix_encoding.ps1
#  Corrige caracteres corruptos en config/settings.py
#  Solo toca las cadenas de texto visibles al usuario,
#  NO modifica lógica ni estructura del código.
# ============================================================

$filePath = Join-Path $PSScriptRoot "config\settings.py"

if (-not (Test-Path $filePath)) {
    Write-Error "No se encontró el archivo: $filePath"
    Write-Host "Asegúrate de ejecutar este script desde la raíz del proyecto (yalu-backend/)"
    exit 1
}

# Leer el archivo como bytes para preservar el encoding exacto
$bytes = [System.IO.File]::ReadAllBytes($filePath)

# Decodificar como Latin-1 (cada byte se mapea 1:1 a su codepoint)
$latin1 = [System.Text.Encoding]::GetEncoding("iso-8859-1")
$utf8    = [System.Text.Encoding]::UTF8

$content = $latin1.GetString($bytes)

# Tabla de reemplazos: texto corrupto -> texto correcto
# (se obtiene al leer bytes UTF-8 como si fueran Latin-1)
$replacements = @{
    "YalÃº"           = "Yalú"
    "LibrerÃ­a"       = "Librería"
    "administraciÃ³n" = "administración"
    "CatÃ¡logo"       = "Catálogo"
    "CategorÃ­as"     = "Categorías"
    "AutenticaciÃ³n"  = "Autenticación"
}

$changed = $false
foreach ($bad in $replacements.Keys) {
    if ($content.Contains($bad)) {
        $content = $content.Replace($bad, $replacements[$bad])
        Write-Host "  Corregido: '$bad'  ->  '$($replacements[$bad])'"
        $changed = $true
    }
}

if ($changed) {
    # Escribir de vuelta en UTF-8 con BOM (igual que el original)
    $utf8bom = New-Object System.Text.UTF8Encoding $true
    [System.IO.File]::WriteAllText($filePath, $content, $utf8bom)
    Write-Host ""
    Write-Host "✅ settings.py corregido correctamente." -ForegroundColor Green
} else {
    Write-Host "ℹ️  No se encontraron caracteres corruptos. El archivo ya está correcto." -ForegroundColor Yellow
}
