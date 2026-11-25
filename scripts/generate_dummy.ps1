# Skrip regenerasi dummy budget.csv dan stock.csv yang selaras dengan data riil sales.csv
# Periode: Sep-Okt 2026 (2 bulan penuh)
$root = Split-Path $PSScriptRoot -Parent
$rng = [System.Random]::new(42)

# Normalisasi alias region
$alias = @{
    'Jabar'       = 'Jawa Barat'
    'JAWA BARAT'  = 'Jawa Barat'
    'JABODETABEK' = 'Jabodetabek'
    'JAWA TIMUR'  = 'Jawa Timur'
}

$salesRaw = Import-Csv "$root\sales.csv"
$sales = $salesRaw | ForEach-Object {
    $reg = $_.region.Trim()
    if ($alias.ContainsKey($reg)) { $reg = $alias[$reg] }
    $_.region = $reg
    $_.branch = $_.branch.Trim()
    $_.brand = $_.brand.Trim()
    $_.sku = $_.sku.Trim()
    $_
}

# Pemetaan unik kode gudang untuk mencegah tabrakan (seperti WH-BDG vs WH-BJM)
$whMap = @{
    'Bandung'       = 'WH-BDG'
    'Banjarmasin'   = 'WH-BJM'
    'Bekasi'        = 'WH-BEK'
    'Jakarta Barat' = 'WH-JKB'
    'Tangerang'     = 'WH-TNG'
    'Cirebon'       = 'WH-CRB'
    'Semarang'      = 'WH-SMG'
    'Solo'          = 'WH-SLO'
    'Malang'        = 'WH-MLG'
    'Surabaya'      = 'WH-SBY'
    'Balikpapan'    = 'WH-BPN'
    'Medan'         = 'WH-MDN'
    'Palembang'     = 'WH-PLM'
}

# 1. GENERATE BUDGET (Sep, Okt, Nov, Des 2026) per region x branch x brand
# Dihitung dari rata-rata bulanan riil (total 2 bulan dibagi 2)
$budgetList = [System.Collections.Generic.List[PSCustomObject]]::new()
$brandBranchGroups = $sales | Group-Object region, branch, brand

foreach ($g in $brandBranchGroups) {
    $first = $g.Group[0]
    $sumNet = ($g.Group | Measure-Object net_sales_idr -Sum).Sum
    $sumQty = ($g.Group | Measure-Object qty_carton -Sum).Sum
    # Baseline bulanan rata-rata dari 2 bulan
    $monthlyNet = [double]$sumNet / 2.0
    $monthlyQty = [double]$sumQty / 2.0

    $mIdx = 0
    foreach ($m in '2026-09', '2026-10', '2026-11', '2026-12') {
        # Faktor variasi target: Sep & Okt baseline, Nov-Des naik tipis
        $growth = 1.0 + (0.02 * $mIdx)
        $factor = $growth * (0.96 + ($rng.NextDouble() * 0.10))
        $bQty = [int][math]::Round($monthlyQty * $factor)
        $bNet = [long]([math]::Round(($monthlyNet * $factor) / 100000.0) * 100000)

        $budgetList.Add([pscustomobject]@{
            period_month         = $m
            entity_code          = 'ID01'
            region               = $first.region
            branch               = $first.branch
            brand                = $first.brand
            sku                  = ''
            budget_qty_carton    = $bQty
            budget_net_sales_idr = $bNet
        })
        $mIdx++
    }
}
$budgetList | Export-Csv "$root\budget.csv" -NoTypeInformation -Encoding utf8 -UseQuotes AsNeeded

# 2. GENERATE STOCK (Snapshot harian 1 Sep - 31 Okt 2026 = 61 hari)
$days = 0..60 | ForEach-Object { (Get-Date '2026-09-01').AddDays($_) }
$stockList = [System.Collections.Generic.List[PSCustomObject]]::new()
$skuBranchGroups = $sales | Group-Object region, branch, brand, sku

foreach ($g in $skuBranchGroups) {
    $first = $g.Group[0]
    $totQty = ($g.Group | Measure-Object qty_carton -Sum).Sum
    $dailyAvg = [math]::Max(1.0, [double]$totQty / 61.0)
    $price = [double]$first.price_per_carton_idr
    $cost = [math]::Round(($price * 0.72) / 1000.0) * 1000
    
    $whCode = if ($whMap.ContainsKey($first.branch)) { $whMap[$first.branch] } else { 'WH-' + $first.branch.Substring(0, 3).ToUpper() }
    $whName = "Gudang $($first.branch)"
    $minStock = [int][math]::Ceiling($dailyAvg * 7.0)
    $onHand = [int]($dailyAvg * (12 + $rng.Next(0, 10)))
    
    # Batch tetap per SKU-Gudang dengan expiry date konsisten (tidak bergeser tiap snapshot)
    $batchCode = 'B2608' + [char](65 + $rng.Next(0, 8))
    $expiryDate = (Get-Date '2026-09-01').AddDays(150 + $rng.Next(0, 120)).ToString('yyyy-MM-dd')

    foreach ($d in $days) {
        $dStr = $d.ToString('yyyy-MM-dd')
        $soldToday = ($g.Group | Where-Object { $_.date -eq $dStr } | Measure-Object qty_carton -Sum).Sum
        if ($null -eq $soldToday) { $soldToday = 0 }
        
        $onHand = [math]::Max(0, $onHand - [int]$soldToday)
        $inTransit = 0
        if ($onHand -lt $minStock) {
            $inTransit = [int]($dailyAvg * 14.0)
            if ($rng.NextDouble() -lt 0.65) {
                $onHand += $inTransit
                $inTransit = 0
            }
        }
        
        $reserved = [int][math]::Min($onHand, [math]::Round($dailyAvg * $rng.NextDouble() * 1.5))
        $stockVal = [long]($onHand * $cost)

        $stockList.Add([pscustomobject]@{
            date                   = $dStr
            entity_code            = 'ID01'
            region                 = $first.region
            branch                 = $first.branch
            warehouse_id           = $whCode
            warehouse_name         = $whName
            brand                  = $first.brand
            sku                    = $first.sku
            batch_no               = $batchCode
            expiry_date            = $expiryDate
            qty_on_hand_carton     = $onHand
            qty_in_transit_carton  = $inTransit
            qty_reserved_carton    = $reserved
            min_stock_carton       = $minStock
            cost_per_carton_idr    = [long]$cost
            stock_value_idr        = $stockVal
        })
    }
}
$stockList | Export-Csv "$root\stock.csv" -NoTypeInformation -Encoding utf8 -UseQuotes AsNeeded

Write-Output "Regenerasi Selesai -> Budget rows: $($budgetList.Count), Stock rows: $($stockList.Count)"
