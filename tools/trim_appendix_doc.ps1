param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath
)

Add-Type -AssemblyName System.IO.Compression.FileSystem

$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("coursework-trim-" + [guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $tempDir | Out-Null

try {
    $workingDocx = Join-Path $tempDir "work.docx"
    Copy-Item -LiteralPath $InputPath -Destination $workingDocx -Force

    $extractDir = Join-Path $tempDir "unzipped"
    [System.IO.Compression.ZipFile]::ExtractToDirectory($workingDocx, $extractDir)

    $documentPath = Join-Path $extractDir "word\document.xml"
    [xml]$doc = [System.IO.File]::ReadAllText($documentPath, [System.Text.Encoding]::UTF8)

    $ns = New-Object System.Xml.XmlNamespaceManager($doc.NameTable)
    $ns.AddNamespace("w", "http://schemas.openxmlformats.org/wordprocessingml/2006/main")

    $body = $doc.SelectSingleNode("//w:body", $ns)
    $appendixParagraph = $null

    foreach ($p in $doc.SelectNodes("//w:body/w:p", $ns)) {
        $text = (($p.SelectNodes(".//w:t", $ns) | ForEach-Object { $_.InnerText }) -join "")
        if ($text.StartsWith("ПРИЛОЖЕНИЕ") -or $text.StartsWith("Приложение А.")) {
            $appendixParagraph = $p
            break
        }
    }

    if (-not $appendixParagraph) {
        throw "Appendix heading was not found."
    }

    $current = $appendixParagraph.NextSibling
    while ($current) {
        $next = $current.NextSibling
        if ($current.LocalName -eq "sectPr") {
            break
        }
        $null = $body.RemoveChild($current)
        $current = $next
    }

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($documentPath, $doc.OuterXml, $utf8NoBom)

    Remove-Item -LiteralPath $workingDocx -Force
    [System.IO.Compression.ZipFile]::CreateFromDirectory($extractDir, $workingDocx)
    Copy-Item -LiteralPath $workingDocx -Destination $InputPath -Force
}
finally {
    if (Test-Path -LiteralPath $tempDir) {
        Remove-Item -LiteralPath $tempDir -Recurse -Force
    }
}
