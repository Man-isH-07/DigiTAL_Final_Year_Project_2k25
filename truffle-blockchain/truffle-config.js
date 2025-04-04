module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "1337", // Matches Ganache's network ID
    },
  },
  compilers: {
    solc: {
      version: "0.6.12", // Match the Solidity version in your contract
    },
  },
};