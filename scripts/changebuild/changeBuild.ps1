param (
    [string]$vcenter = "vcenter-ito-lab.spirenteng.com",
    [string]$vel = "Empty",
    [string]$velbuild="Empty",
    [string]$ite="Empty",
    [string]$itebuild="Empty",
    [string]$agent="Empty",
    [string]$agentbuild="Empty",
    [string]$version="7.3.0",
    [string]$user="",
    [string]$password=""
 )

$version = "v$version"
###Connect to vCenter###
Connect-VIServer -Server $vcenter -User $user -Password $password

function sortingArray 
{
    param([string[]]$arr)
    $arr = $arr.replace(".iso","")
    $new = [string[]]$arr|%{[int]"$_"} | sort-object | select -last 1
    return $new
}

###Set given or last build for ITE### 
if ( $ite -ne "Empty")
{
	if( $itebuild -ne "Empty")
	{
		$iteIso = "ite\${version}\build\${itebuild}.iso"
	}
	else
	{
		# ###Get last build for ITE###
		$result = get-childitem vmstore:\Sunnyvale-Lab\live-iso\ite\${version}\build -Recurse -Include *.iso | Select Name
		if ( $result.length -gt 1 )
		{
			$result = sortingArray $result.name
			$itebuild = [string]$result + ".iso"
		}
		else
		{
			$itebuild = $result.name
		}
		$iteIso = "ite\${version}\build\${itebuild}"
	}
	###Power off ite and change build
	if( $(get-vm $ite).PowerState -ne "PoweredOff" )
	{
		stop-vm $ite -confirm:$false 
	}
	Get-CDDrive $ite | Set-CDDrive -IsoPath "[live-iso] ${iteIso}" -Confirm:$false
	##Power on ITE and wait for it to boot###
	start-vm $ite -confirm:$false
	sleep 120
}

###Set given or last build for Agent### 
if ( $agent -ne "Empty" )
{
	if( $agentbuild -ne "Empty" )
	{
		$agentIso = "vel-agent\${version}\build\${agentbuild}.iso"
	}
	else
	{
		# ###Get last build for ITE###
		$result = get-childitem vmstore:\Sunnyvale-Lab\live-iso\vel-agent\${version}\build -Recurse -Include *.iso | Select Name
		if ( $result.length -gt 1 )
		{
			$result = sortingArray $result.name
			$agentbuild = [string]$result + ".iso"
		}
		else
		{
			$agentbuild = $result.name
		}
		$agentIso = "vel-agent\${version}\build\${agentbuild}"
	}
	###Power off agent and change build
	if( $(get-vm $agent).PowerState -ne "PoweredOff" )
	{
		stop-vm $agent -confirm:$false
	}
	Get-CDDrive $agent | Set-CDDrive -IsoPath "[live-iso] ${agentIso}" -Confirm:$false
	##Power on Agent###
	start-vm $agent -confirm:$false
}

###Set given or last build for Velocity### 
if ( $vel -ne "Empty" )
{
	if( $velbuild -ne "Empty")
	{
		$velIso = "vel\${version}\build\${velbuild}.iso"
	}
	else
	{
		###Get last build for Velocity###
		$result = get-childitem vmstore:\Sunnyvale-Lab\live-iso\vel\${version}\build -Recurse -Include *.iso | Select Name
		if( $result.length -gt 1 )
		{
			$result = sortingArray $result.name
			$velbuild = [string]$result + ".iso"
		}
		else
		{
			$velbuild = $result.name
		}
		$velIso = "vel\${version}\build\${velbuild}"
	}
	###Power off velo and change build
	if( $(get-vm $vel).PowerState -ne "PoweredOff" )
	{
		stop-vm $vel -confirm:$false
	}
	Get-CDDrive $vel | Set-CDDrive -IsoPath "[live-iso] ${velIso}" -Confirm:$false
	##Power on Velocity once ITE is up and running###
	start-vm $vel -confirm:$false
	do {
		$url = "https://" + $vel + ".spirenteng.com/velocity/api/auth/v2/token"
		$credPair = "spirent:spirent"
		$encodedCredentials = [System.Convert]::ToBase64String([System.Text.Encoding]::ASCII.GetBytes($credPair))
		$headers = @{ Authorization = "Basic $encodedCredentials" }
		$response = try { 
    	(Invoke-WebRequest -Uri $url -Method Get -Headers $headers -UseBasicParsing -ErrorAction Stop).BaseResponse
		} catch [System.Net.WebException] { 
    	Write-Verbose "An exception was caught: $($_.Exception.Message)"
    	$_.Exception.Response 
		}

		if ( $response.statuscode -ne "OK" ) 
		{
			start-sleep -seconds 30
		}
	}
	while( $response.statuscode -ne "OK" )
}

###Exit pwsh###
# exit
