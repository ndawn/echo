apt update
apt install apt-transport-https ca-certificates curl gnupg lsb-release git -y
rm -rf /usr/share/keyrings/docker-archive-keyring.gpg
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install docker-ce docker-ce-cli containerd.io docker-compose -y
service docker start
git clone https://github.com/ndawn/echo-agent.git
cp config.json echo-agent/echo_agent
cd echo-agent
docker-compose up --build -d
cd -
