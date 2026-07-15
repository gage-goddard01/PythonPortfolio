# Python Portfolio

A Flask-based portfolio website that showcases my Python applications, AWS deployment experience, and cybersecurity learning projects.

The site is hosted on an Amazon EC2 instance and uses Gunicorn and Nginx for production deployment.

## Live Website

The portfolio is currently available at:

http://44.200.37.77

> The public IP may change if the EC2 instance is stopped and restarted.

## Features

- Professional Flask portfolio homepage
- Shared navigation using Flask template inheritance
- Responsive CSS styling
- Interactive Rock, Paper, Scissors game
- Projects page for future Python applications
- Production deployment on AWS EC2
- Automatic startup using systemd
- Nginx reverse proxy
- Gunicorn application server

## Technologies Used

- Python
- Flask
- HTML
- CSS
- Jinja
- Gunicorn
- Nginx
- Ubuntu Linux
- AWS EC2
- systemd
- Git
- GitHub
- VS Code Remote SSH

## Project Structure

```text
PythonPortfolio/
├── app.py
├── requirements.txt
├── README.md
├── apps/
│   └── rock_paper_scissors.py
├── static/
│   ├── css/
│   │   └── style.css
│   ├── images/
│   └── js/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── projects.html
│   ├── rps.html
│   ├── about.html
│   └── contact.html
└── test.py