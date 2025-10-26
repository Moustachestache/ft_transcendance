# ft_transcendence

A full-stack web application featuring a real-time multiplayer Pong game with modern web technologies. Final project of the 42 School common core curriculum.

## 🎮 Overview

ft_transcendence is a single-page application (SPA) that allows users to play Pong online with friends, manage their profile, and interact through a chat system. This project demonstrates proficiency in full-stack development, real-time communication, and containerized deployment.

## ✨ Key Features

- **Real-time Multiplayer Pong**: Play classic Pong against other users with WebSocket-based gameplay
- **User Management**: Registration, authentication, and customizable user profiles
- **Live Chat**: Real-time messaging system with channels and direct messages
- **Matchmaking System**: Queue system for finding opponents
- **Game History & Statistics**: Track your performance and view match history
- **Friend System**: Add friends and challenge them to matches
- **Responsive Design**: Optimized for various screen sizes

## 🛠️ Tech Stack

**Frontend:**
- Vanilla JS
- HTML5 Canvas for game rendering
- WebSocket for real-time communication

**Backend:**
- Django
- PostgreSQL database
- WebSocket server for game state management

**DevOps:**
- Docker & Docker Compose

## 🚀 Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Moustachestache/ft_transcendance.git
cd ft_transcendance
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Build and run with Docker:
```bash
docker-compose up --build
```

4. Access the application at `http://localhost:8080`

## 📁 Project Structure

```
[Customize based on your actual structure]
├── frontend/          # Frontend application
├── backend/           # Backend API and game server
├── database/          # Database configurations
├── docker-compose.yml # Container orchestration
└── README.md
```

## 🎯 42 School Requirements

This project fulfills all mandatory requirements of the ft_transcendence project, including:
- Web framework implementation
- Database integration
- User authentication
- Real-time multiplayer game
- Standard security practices

This project is part of the 42 School curriculum. 

*Note: This is a cloned version of our original private group repository for portfolio purposes.*
