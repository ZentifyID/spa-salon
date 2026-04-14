param(
    [Parameter(Mandatory = $true)]
    [string]$InputPath,

    [Parameter(Mandatory = $true)]
    [string]$ContentPath
)

Add-Type -AssemblyName System.IO.Compression.FileSystem

$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("coursework-docx-" + [guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $tempDir | Out-Null

try {
    $contentJson = [System.IO.File]::ReadAllText($ContentPath, [System.Text.Encoding]::UTF8)
    $content = $contentJson | ConvertFrom-Json

    $workingDocx = Join-Path $tempDir "work.docx"
    Copy-Item -LiteralPath $InputPath -Destination $workingDocx -Force

    $extractDir = Join-Path $tempDir "unzipped"
    [System.IO.Compression.ZipFile]::ExtractToDirectory($workingDocx, $extractDir)

    $documentPath = Join-Path $extractDir "word\document.xml"
    [xml]$doc = [System.IO.File]::ReadAllText($documentPath, [System.Text.Encoding]::UTF8)

    $nsUri = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    $ns = New-Object System.Xml.XmlNamespaceManager($doc.NameTable)
    $ns.AddNamespace("w", $nsUri)

    $body = $doc.SelectSingleNode("//w:body", $ns)
    $sectPr = $doc.SelectSingleNode("//w:body/w:sectPr", $ns)

    function Get-ParagraphByTextPrefix {
        param([string]$Prefix)

        foreach ($p in $doc.SelectNodes("//w:body/w:p", $ns)) {
            $text = (($p.SelectNodes(".//w:t", $ns) | ForEach-Object { $_.InnerText }) -join "")
            if ($text.StartsWith($Prefix)) {
                return $p
            }
        }

        throw "Paragraph with prefix '$Prefix' was not found."
    }

    function New-ParagraphFromTemplate {
        param(
            [System.Xml.XmlElement]$TemplateParagraph,
            [string]$Text
        )

        $newParagraph = $TemplateParagraph.CloneNode($true)

        foreach ($xpath in @(".//w:fldChar", ".//w:instrText", "./w:hyperlink", "./w:proofErr", "./w:bookmarkStart", "./w:bookmarkEnd")) {
            $nodes = $newParagraph.SelectNodes($xpath, $ns)
            foreach ($node in @($nodes)) {
                $null = $node.ParentNode.RemoveChild($node)
            }
        }

        $runs = $newParagraph.SelectNodes("./w:r", $ns)
        foreach ($run in @($runs)) {
            $null = $newParagraph.RemoveChild($run)
        }

        $templateRun = $TemplateParagraph.SelectSingleNode("./w:r", $ns)
        if (-not $templateRun) {
            throw "Template paragraph does not contain a run."
        }

        $run = $templateRun.CloneNode($true)
        foreach ($xpath in @(".//w:tab", ".//w:br", ".//w:t")) {
            $nodes = $run.SelectNodes($xpath, $ns)
            foreach ($node in @($nodes)) {
                $null = $node.ParentNode.RemoveChild($node)
            }
        }

        $textNode = $doc.CreateElement("w", "t", $nsUri)
        if ($Text.StartsWith(" ") -or $Text.EndsWith(" ")) {
            $spaceAttr = $doc.CreateAttribute("xml", "space", "http://www.w3.org/XML/1998/namespace")
            $spaceAttr.Value = "preserve"
            $null = $textNode.Attributes.Append($spaceAttr)
        }
        $textNode.InnerText = $Text
        $null = $run.AppendChild($textNode)
        $null = $newParagraph.AppendChild($run)

        return $newParagraph
    }

    function Insert-BeforeSection {
        param([object[]]$Paragraphs)

        foreach ($entry in $Paragraphs) {
            $template = Get-ParagraphByTextPrefix $entry.templatePrefix
            $newParagraph = New-ParagraphFromTemplate -TemplateParagraph $template -Text $entry.text
            $null = $body.InsertBefore($newParagraph, $sectPr)
        }
    }

    function Insert-AfterParagraph {
        param([object[]]$Paragraphs)

        foreach ($entry in $Paragraphs) {
            $afterParagraph = Get-ParagraphByTextPrefix $entry.afterPrefix
            $template = Get-ParagraphByTextPrefix $entry.templatePrefix
            $newParagraph = New-ParagraphFromTemplate -TemplateParagraph $template -Text $entry.text
            $nextNode = $afterParagraph.NextSibling
            if ($nextNode) {
                $null = $body.InsertBefore($newParagraph, $nextNode)
            }
            else {
                $null = $body.InsertBefore($newParagraph, $sectPr)
            }
        }
    }

    Insert-AfterParagraph -Paragraphs $content.insertAfter
    Insert-BeforeSection -Paragraphs $content.appendToEnd

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
