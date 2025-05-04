import React from 'react';
import { Card, Alert } from 'react-bootstrap';

function Instructions() {
  return (
    <Card className="p-4 shadow-sm">
      <Card.Body>
        <h3 className="text-center mb-4 heading">How to Use LiverCare AI</h3>
        <Card.Text>
          LiverCare AI specializes in diagnosing liver diseases using advanced AI-powered models trained exclusively on histopathological image datasets.
        </Card.Text>
        <Alert variant="info" className="mt-3">
          <strong>What You Can Do:</strong>
          <ul>
            <li>Upload high-quality histopathological images of liver tissue in JPEG or PNG format.</li>
            <li>Obtain a diagnosis with detailed condition classification and confidence scores.</li>
          </ul>
        </Alert>
        <Alert variant="warning" className="mt-3">
          <strong>Important Note:</strong>
          <ul>
            <li>Currently, our system supports <i>only histopathological liver images</i>. Other types of images will not yield accurate results.</li>
            <li>Ensure images are well-lit and clear for optimal performance.</li>
          </ul>
        </Alert>
        <Card.Text className="mt-3">
          We are continuously enhancing our system to support additional data types in the future. Stay tuned for updates!
        </Card.Text>
      </Card.Body>
    </Card>
  );
}

export default Instructions;
