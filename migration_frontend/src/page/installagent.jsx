import React, { useState, useEffect } from 'react';

const InstallAgentForm = () => {
  const [awsKey, setAwsKey] = useState('');
  const [secretKey, setSecretKey] = useState('');
  const [vms, setVms] = useState([{ ip: '', username: '', password: '' }]);
  const [output, setOutput] = useState('');
  const [installTriggered, setInstallTriggered] = useState(false);
  const [systemType, setSystemType] = useState('linux'); // State to store system type

  useEffect(() => {
    const installAgent = async () => {
      if (!installTriggered) return;

      try {
        const apiUrl = systemType === 'windows' 
          ? 'http://127.0.0.1:5000/install_agent_windows' 
          : 'http://127.0.0.1:5000/install_agent_linux';

        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            awsKey,
            secretKey,
            vms,
          }),
        });

        if (response.ok) {
          setOutput('install success');
        } else {
          setOutput('install failed');
        }
      } catch (error) {
        setOutput('install failed');
      } finally {
        setInstallTriggered(false);
      }
    };

    installAgent();
  }, [installTriggered, awsKey, secretKey, vms, systemType]);

  const handleAddVm = () => {
    setVms([...vms, { ip: '', username: '', password: '' }]);
  };

  const handleVmChange = (index, field, value) => {
    const updatedVms = [...vms];
    updatedVms[index][field] = value;
    setVms(updatedVms);
  };

  const handleInstallAgent = () => {
    setInstallTriggered(true);
  };

  const handleSystemTypeChange = (type) => {
    setSystemType(type);
    setOutput(''); // Clear output when switching system type
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h2>Install discovery agent for VM</h2>
      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={() => handleSystemTypeChange('windows')} 
          style={{ backgroundColor: systemType === 'windows' ? '#ccc' : '' }}
        >
          Windows
        </button>
        <button 
          onClick={() => handleSystemTypeChange('linux')} 
          style={{ marginLeft: '10px', backgroundColor: systemType === 'linux' ? '#ccc' : '' }}
        >
          Linux
        </button>
      </div>
      <div style={{ marginBottom: '20px' }}>
        <h3>AWS credentials</h3>
        <input
          type="text"
          placeholder="aws key"
          value={awsKey}
          onChange={(e) => setAwsKey(e.target.value)}
          style={{ display: 'block', marginBottom: '10px' }}
        />
        <input
          type="text"
          placeholder="secret access key"
          value={secretKey}
          onChange={(e) => setSecretKey(e.target.value)}
          style={{ display: 'block', marginBottom: '10px' }}
        />
      </div>
      <div style={{ marginBottom: '20px' }}>
        <h3>VM details ({systemType.charAt(0).toUpperCase() + systemType.slice(1)})</h3>
        {vms.map((vm, index) => (
          <div key={index} style={{ marginBottom: '10px', border: '1px solid #ccc', padding: '10px' }}>
            <h4>VM {index + 1}</h4>
            <input
              type="text"
              placeholder="ip address"
              value={vm.ip}
              onChange={(e) => handleVmChange(index, 'ip', e.target.value)}
              style={{ display: 'block', marginBottom: '5px' }}
            />
            <input
              type="text"
              placeholder="username"
              value={vm.username}
              onChange={(e) => handleVmChange(index, 'username', e.target.value)}
              style={{ display: 'block', marginBottom: '5px' }}
            />
            <input
              type="password"
              placeholder="password"
              value={vm.password}
              onChange={(e) => handleVmChange(index, 'password', e.target.value)}
              style={{ display: 'block', marginBottom: '5px' }}
            />
          </div>
        ))}
        <button onClick={handleAddVm}>Add more VM</button>
      </div>
      <button onClick={handleInstallAgent} style={{ marginBottom: '20px' }}>
        Start Install Agent
      </button>
      <div>
        Output: <span style={{ color: output === 'install success' ? 'green' : 'red' }}>{output}</span>
      </div>
    </div>
  );
};

export default InstallAgentForm;
