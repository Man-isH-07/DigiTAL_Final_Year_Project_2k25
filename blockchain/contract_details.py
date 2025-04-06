# blockchain/contract_details.py
CONTRACT_ADDRESS = "0x8CdaF0CD259887258Bc13a92C0a6dA92698644C0"  # From Truffle deployment
CONTRACT_ABI = [
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "recordId",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "dataHash",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "recordType",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "patientEmail",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "doctorId",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "name": "RecordAdded",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "recordCount",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "records",
      "outputs": [
        {
          "internalType": "string",
          "name": "dataHash",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "recordType",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "patientEmail",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "doctorId",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "timestamp",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_dataHash",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_recordType",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_patientEmail",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "_doctorId",
          "type": "uint256"
        }
      ],
      "name": "addRecord",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_recordId",
          "type": "uint256"
        }
      ],
      "name": "getRecord",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    }
  ]