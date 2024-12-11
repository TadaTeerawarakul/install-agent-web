from flask import Flask, request, jsonify
import paramiko
import time
from pypsrp.client import Client
from pypsrp.exceptions import WinRMError
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Route แรก
@app.route('/')
def home():
    return "Welcome to Flask Backend Server!"

# Route สำหรับ API
@app.route('/api/data', methods=['GET'])
def get_data():
    sample_data = {
        "message": "This is sample data",
        "status": "success"
    }
    return jsonify(sample_data)

# Route สำหรับรับข้อมูลแบบ POST
@app.route('/api/data', methods=['POST'])
def post_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    return jsonify({"received_data": data, "status": "success"})

@app.route('/install_agent_linux', methods=['POST'])
def install_agent_linux():
    try:
        # Parse JSON data from request
        data = request.get_json()
        
        aws_key_id = data.get('awsKey')  # Matches 'awsKey' from frontend
        aws_key_secret = data.get('secretKey')  # Matches 'secretKey' from frontend
        vms = data.get('vms', [])  # List of VMs

        if not aws_key_id or not aws_key_secret or not vms:
            return jsonify({"error": "Invalid input, missing AWS credentials or VM details"}), 400
        
        # Commands to execute on the VMs
        commands = [
            "curl -o ./aws-discovery-agent.tar.gz https://s3-us-west-2.amazonaws.com/aws-discovery-agent.us-west-2/linux/latest/aws-discovery-agent.tar.gz",
            "tar -xzf aws-discovery-agent.tar.gz",
            f"sudo bash install -r us-east-1 -k {aws_key_id} -s {aws_key_secret}"
        ]

        results = []

        #Iterate through each VM and attempt installation
        for vm in vms:
            ip = vm.get('ip')
            username = vm.get('username')
            password = vm.get('password')

            if not ip or not username or not password:
                results.append({"ip": ip, "status": "failed", "error": "Invalid VM details"})
                continue

            try:
                # Setup SSH client
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # Connect to the VM
                ssh.connect(ip, username=username, password=password)
                
                # Open interactive shell and execute commands
                shell = ssh.invoke_shell()
                
                # Elevate to sudo
                shell.send('sudo -i\n')
                time.sleep(2)
                shell.send(f'{password}\n')
                time.sleep(2)
                
                for command in commands:
                    shell.send(f'{command}\n')
                    time.sleep(10)  # Wait for command to execute
                
                # Close the SSH connection
                ssh.close()
                results.append({"ip": ip, "status": "success"})
            
            except Exception as e:
                results.append({"ip": ip, "status": "failed", "error": str(e)})

        return jsonify({"results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/install_agent_windows', methods=['POST'])
def install_agent_windows():
    try:
        # Receive data from the request body
        data = request.get_json()
        aws_key_id = data.get('awsKey')
        aws_secret_key = data.get('secretKey')
        vms = data.get('vms', [])

        if not aws_key_id or not aws_secret_key or not vms:
            return jsonify({"error": "Missing required AWS credentials or VM details"}), 400

        # Corrected PowerShell command template
        command_template = (
            f"powershell -Command \"& {{ "
            f"Invoke-WebRequest -Uri 'https://s3-us-west-2.amazonaws.com/aws-discovery-agent.us-west-2/windows/latest/AWSDiscoveryAgentInstaller.exe' -OutFile 'AWSDiscoveryAgentInstaller.exe'; "
            f".\\AWSDiscoveryAgentInstaller.exe REGION='us-east-1' KEY_ID='{aws_key_id}' KEY_SECRET='{aws_secret_key}' /q; "
            f"}}\""
        )

        results = []

        # Loop through each VM and execute the PowerShell command
        for vm in vms:
            ip = vm.get('ip')
            username = vm.get('username')
            password = vm.get('password')

            if not ip or not username or not password:
                results.append({"ip": ip, "status": "failed", "error": "Invalid VM details"})
                continue

            try:
                # Create a client for the remote host
                client = Client(ip, username=username, password=password, ssl=False)

                # Execute the PowerShell command
                stdout, stderr, rc = client.execute_cmd(command_template)

                # Store the result
                results.append({
                    "ip": ip,
                    "status": "success" if rc == 0 else "failed",
                    "stdout": stdout.strip(),
                    "stderr": stderr.strip(),
                    "return_code": rc
                })

            except WinRMError as e:
                results.append({"ip": ip, "status": "failed", "error": str(e)})

        return jsonify({"results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Start Server
if __name__ == '__main__':
    app.run(debug=True)
