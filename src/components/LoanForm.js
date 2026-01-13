import React, { useState } from 'react';
import axios from 'axios';
import { Form, Button } from 'react-bootstrap';

const LoanForm = () => {
  const [formData, useFormData] = useState({
    loan_id: '', borrower_name: '', loan_amount: '', project_type: '', description: '', borrower_address: ''
  });

  const handleChange = (e) => useFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:5000/api/loans', formData);
      alert('Loan created!');
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  return (
    <Form onSubmit={handleSubmit}>
      <Form.Group><Form.Label>Loan ID</Form.Label><Form.Control name="loan_id" onChange={handleChange} /></Form.Group>
      <Form.Group><Form.Label>Borrower Name</Form.Label><Form.Control name="borrower_name" onChange={handleChange} /></Form.Group>
      <Form.Group><Form.Label>Loan Amount</Form.Label><Form.Control name="loan_amount" type="number" onChange={handleChange} /></Form.Group>
      <Form.Group><Form.Label>Project Type</Form.Label><Form.Control name="project_type" onChange={handleChange} /></Form.Group>
      <Form.Group><Form.Label>Description</Form.Label><Form.Control name="description" onChange={handleChange} /></Form.Group>
      <Form.Group><Form.Label>Borrower Address (EVM)</Form.Label><Form.Control name="borrower_address" onChange={handleChange} /></Form.Group>
      <Button type="submit">Create Loan</Button>
    </Form>
  );
};

export default LoanForm;
