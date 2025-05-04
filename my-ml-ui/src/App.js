import React from 'react';
import { Container, Navbar, Nav } from 'react-bootstrap';
import { BrowserRouter as Router, Route, Switch, Link, NavLink } from 'react-router-dom';
import { FaHeartbeat } from 'react-icons/fa';
import About from './About';
import Diagnostic from './Diagnostic';
import Contact from './Contact';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-wrapper">
        <Navbar bg="info" variant="dark" expand="lg" sticky="top">
          <Container fluid>
            <Navbar.Brand as={Link} to="/" className="brand">
              <FaHeartbeat className="brand-icon" />
              LiverCare AI
            </Navbar.Brand>

            <Navbar.Toggle aria-controls="basic-navbar-nav" />

            <Navbar.Collapse id="basic-navbar-nav">
              <Nav className="ms-auto">
                <Nav.Link as={NavLink} exact to="/">
                  About
                </Nav.Link>
                <Nav.Link as={NavLink} to="/diagnostic">
                  Diagnostic
                </Nav.Link>
                <Nav.Link as={NavLink} to="/contact">
                  Contact
                </Nav.Link>
              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        <Container className="main-content">
          <Switch>
            <Route exact path="/" component={About} />
            <Route path="/diagnostic" component={Diagnostic} />
            <Route path="/contact" component={Contact} />
          </Switch>
        </Container>

        <footer className="footer">
          <Container>
            <p>&copy; 2025 LiverCare AI. All rights reserved.</p>
            <small>
              <Link to="/privacy-policy">Privacy Policy</Link> |{' '}
              <Link to="/terms-of-service">Terms of Service</Link>
            </small>
          </Container>
        </footer>
      </div>
    </Router>
  );
}

export default App;
