 import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import LoanForm from './components/LoanForm';
import LoanList from './components/LoanList';
import RealTimeUpdates from './components/RealTimeUpdates';
// Import ScoreCalculator and use in list rows as needed

function App() {
  return (
    <div className="App">
      <h1>EcoScore Finance</h1>
      <LoanForm />
      <LoanList />
      <RealTimeUpdates />
    </div>
  );
}

export default App;
