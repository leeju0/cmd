1. WSL에서 서비스 바인딩 확인
ss -ltn '( sport = :8005 )'
hostname -I
127.0.0.1:8005로만 수신 중이면 서비스 설정을 0.0.0.0:8005로 바꾸고 재시작하세요. Uvicorn이라면 기존 실행 명령에 --host 0.0.0.0 --port 8005를 지정하면 됩니다.

2. Windows 서버의 관리자 PowerShell에서 포트 전달 및 방화벽 등록

아래 IP 두 개를 실제 값으로 바꾸세요. hostname -I에 IP가 여러 개 나오면 WSL의 eth0 IPv4를 사용하세요.
$serverIp = "176.16.x.x"  # Windows 서버 IP
$wslIp = "172.x.x.x"      # WSL 내부 IP

Test-NetConnection -ComputerName $wslIp -Port 8005

netsh interface portproxy add v4tov4 listenaddress=$serverIp listenport=8005 connectaddress=$wslIp connectport=8005

New-NetFirewallRule -DisplayName "WSL TCP 8005" -Direction Inbound -Action Allow -Protocol TCP -LocalAddress $ser
