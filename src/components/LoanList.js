import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Table } from 'react-bootstrap';

const LoanList = () => {
  const [loans, setLoans] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:5000/api/loans').then(res => setLoans(res.data.loans));
  }, []);

  return (
    <Table striped bordered hover>
      <thead><tr><th>ID</th><th>Borrower</th><th>Amount</th><th>Type</th><th>Score</th><th>Status</th></tr></thead>
      <tbody>
        {loans.map(loan => (
          <tr key={loan.loan_id}>
            <td>{loan.loan_id}</td><td>{loan.borrower_name}</td><td>{loan.loan_amount}</td>
            <td>{loan.project_type}</td><td>{loan.eco_score}</td><td>{loan.status}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default LoanList;
