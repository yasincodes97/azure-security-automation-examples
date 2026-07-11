// Suspicious Sign-In Detection
// Detects impossible travel and unusual location sign-ins using SigninLogs
// Table: SigninLogs (Microsoft Entra ID / Azure AD Sign-in logs)

SigninLogs
| where TimeGenerated > ago(7d)
| where ResultType == "0" // successful sign-ins only
| project TimeGenerated, UserPrincipalName, AppDisplayName, IPAddress,
          Location = tostring(LocationDetails.city),
          Country = tostring(LocationDetails.countryOrRegion),
          DeviceDetail = tostring(DeviceDetail.displayName)
| summarize
    SignInCount = count(),
    DistinctCountries = dcount(Country),
    Countries = make_set(Country),
    FirstSeen = min(TimeGenerated),
    LastSeen = max(TimeGenerated)
    by UserPrincipalName
| where DistinctCountries > 1
| extend TimeBetweenSignins = LastSeen - FirstSeen
| where TimeBetweenSignins < 2h // flag rapid cross-country sign-ins
| project UserPrincipalName, Countries, DistinctCountries, TimeBetweenSignins, FirstSeen, LastSeen
| order by TimeBetweenSignins asc
