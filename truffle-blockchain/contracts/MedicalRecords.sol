// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;

contract MedicalRecords {
    struct Record {
        string dataHash;
        string recordType;
        string patientEmail;
        uint256 doctorId;
        uint256 timestamp;
    }

    mapping(uint256 => Record) public records;
    uint256 public recordCount;

    event RecordAdded(uint256 recordId, string dataHash, string recordType, string patientEmail, uint256 doctorId, uint256 timestamp);

    function addRecord(
        string memory _dataHash,
        string memory _recordType,
        string memory _patientEmail,
        uint256 _doctorId
    ) public {
        recordCount++;
        records[recordCount] = Record(
            _dataHash,
            _recordType,
            _patientEmail,
            _doctorId,
            block.timestamp
        );
        emit RecordAdded(recordCount, _dataHash, _recordType, _patientEmail, _doctorId, block.timestamp);
    }

    function getRecord(uint256 _recordId) public view returns (string memory, string memory, string memory, uint256, uint256) {
        Record memory record = records[_recordId];
        return (record.dataHash, record.recordType, record.patientEmail, record.doctorId, record.timestamp);
    }
}