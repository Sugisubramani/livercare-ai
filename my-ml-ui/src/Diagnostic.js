import React, { useState, useRef } from 'react';
import { Card, Form, Button, Alert, Spinner, Row, Col } from 'react-bootstrap';
import axios from 'axios';

function Diagnostic() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const fileInputRef = useRef(null); // added ref here

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];

    if (!file || !allowedTypes.includes(file.type)) {
      setError("Only JPEG or PNG histopathological images are supported.");
      setSelectedFile(null);
      setPreviewUrl(null);
      return;
    }

    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setPrediction(null);
    setError("");
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a histopathological image to upload.");
      return;
    }

    setLoading(true);
    setError("");
    setPrediction(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await axios.post("http://localhost:8000/predict", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setPrediction(response.data);
    } catch (err) {
      setError("Diagnosis retrieval failed. Please try again later.");
      console.error(err);
    }

    setLoading(false);
  };

  return (
    <div style={{ maxWidth: "600px", margin: "20px auto", paddingBottom: "20px" }}>
      <Card className="p-3 shadow-sm">
        <Card.Body>
          <h4 className="text-center mb-3 heading">Liver Disease Detection</h4>

          <Form.Group controlId="formFile" className="mb-3">
            <Form.Label>Upload a Histopathological Image</Form.Label>
            <div className="d-flex align-items-center gap-2">
              <Form.Control 
                type="file" 
                accept="image/*" 
                onChange={handleFileChange} 
                disabled={loading}
                ref={fileInputRef} // linked input to ref
              />
              {selectedFile && (
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => {
                    setSelectedFile(null);
                    setPreviewUrl(null);
                    setPrediction(null);
                    if (fileInputRef.current) {
                      fileInputRef.current.value = ""; // clear file input
                    }
                  }}
                >
                  -
                </Button>
              )}
            </div>
          </Form.Group>

          <div className="d-grid mb-3">
            <Button variant="primary" onClick={handleUpload} disabled={loading}>
              {loading ? (
                <>
                  <Spinner animation="border" size="sm" /> Processing...
                </>
              ) : (
                "Get Diagnosis"
              )}
            </Button>
          </div>

          {previewUrl && (
            <Row className="mb-3 align-items-center">
              <Col sm={6} className="text-center">
                <img
                  src={previewUrl}
                  alt="Preview"
                  style={{
                    maxWidth: "100%",
                    height: "auto",
                    maxHeight: "200px",
                    objectFit: "contain",
                    borderRadius: "8px",
                  }}
                />
              </Col>

              {prediction && (
                <Col sm={6}>
                  <Alert variant="success">
                    <strong>Condition:</strong> {prediction.predicted_class}
                  </Alert>
                  <Alert variant="success">
                    <strong>Confidence:</strong> {prediction.confidence.toFixed(2)}%
                  </Alert>
                </Col>
              )}
            </Row>
          )}

          {error && (
            <Alert variant="danger">
              {error}
            </Alert>
          )}
        </Card.Body>
      </Card>
    </div>
  );
}

export default Diagnostic;
