module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "1337"  // Use a fixed network ID
    }
  },
  compilers: {
    solc: {
      version: "0.6.12",
    }
  },
  contracts_build_directory: "./build/contracts"
};