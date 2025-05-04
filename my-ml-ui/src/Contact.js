// Contact.js
import React from 'react';
import { Card } from 'react-bootstrap';

function Contact() {
  return (
    <Card className="p-4 shadow-sm">
      <Card.Body>
        <h3 className="text-center mb-4 heading">Contact Us</h3>
        <p className="text-center">
          Have questions, need support, or want to collaborate? We’re here for you.
        </p>
        <p className="text-center">
          <strong>Email:</strong> <a href="mailto:support@livercareai.com" className="theme-link">support@livercareai.com</a>
        </p>
        <p className="text-center">
          <strong>Phone:</strong> +91 98765 43***
        </p>
        <p className="text-center">
          Our team aims to respond within 24 hours. Your feedback and inquiries are valuable to us!
        </p>
      </Card.Body>
    </Card>
  );
}

export default Contact;
