// High-Severity Vulnerability Triage
// Surfaces High/Critical CVSS vulnerabilities from Microsoft Defender for Endpoint
// with exploit availability, joined against device criticality context.
// Tables: DeviceTvmSoftwareVulnerabilities, DeviceInfo (Advanced Hunting)

DeviceTvmSoftwareVulnerabilities
| where TimeGenerated > ago(1d)
| where VulnerabilitySeverityLevel in ("High", "Critical")
| where IsExploitAvailable == true
| project DeviceId, DeviceName, CveId, VulnerabilitySeverityLevel,
          SoftwareName, SoftwareVendor, RecommendedSecurityUpdate
| join kind=inner (
    DeviceInfo
    | where TimeGenerated > ago(1d)
    | summarize arg_max(TimeGenerated, OSPlatform, DeviceId) by DeviceId
    | project DeviceId, OSPlatform
) on DeviceId
| where OSPlatform != "Android" // exclude mobile devices per posture scoping
| summarize
    AffectedDevices = dcount(DeviceId),
    Devices = make_set(DeviceName, 10)
    by CveId, VulnerabilitySeverityLevel, SoftwareName
| order by AffectedDevices desc
