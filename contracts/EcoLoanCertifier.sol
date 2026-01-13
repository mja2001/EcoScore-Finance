// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EcoLoanCertifier {
    mapping(uint => uint) public loanEcoScores;
    event LoanCertified(uint indexed loanId, uint ecoScore, address borrower);

    function certifyLoan(uint loanId, uint ecoScore, address borrower) public {
        require(ecoScore > 80, "EcoScore must be above 80 to certify");
        loanEcoScores[loanId] = ecoScore;
        emit LoanCertified(loanId, ecoScore, borrower);
    }

    function getEcoScore(uint loanId) public view returns (uint) {
        return loanEcoScores[loanId];
    }
}
