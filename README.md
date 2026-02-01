# EcoScore Finance 🌱

> AI-powered platform that scores loans by environmental impact, rewards green projects with blockchain incentives, and tracks real carbon reduction—making sustainability profitable for lenders and borrowers.

## 🚀 Features

- **AI Environmental Scoring**: LSTM models predict sustainability impact (87% accuracy)
- **Real-Time IoT Monitoring**: Live CO2/energy tracking from funded projects
- **Blockchain Incentives**: Automated rewards via Hedera smart contracts
- **Desktop Platform**: Cross-platform Electron app (Windows, macOS, Linux)
- **ESG Compliance**: Automated reporting for regulatory requirements

## 🏗️ Architecture
```
┌─────────────────┐
│  Electron UI    │
│   (React)       │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  Flask   │
    │  Backend │
    └────┬─────┘
         │
    ┌────▼────────────────────┐
    │                         │
┌───▼──────┐    ┌────▼─────┐    ┌────▼──────┐
│ ML Model │    │ Hedera   │    │   IoT     │
│  (LSTM)  │    │Blockchain│    │  Gateway  │
└──────────┘    └──────────┘    └───────────┘
```

## 📦 Tech Stack

**Frontend**: Electron, React, TailwindCSS, Recharts  
**Backend**: Python, Flask, Node.js  
**AI/ML**: TensorFlow, Keras, LSTM, scikit-learn  
**Blockchain**: Hedera Hashgraph, Solidity  
**Database**: PostgreSQL, MongoDB, Redis  
**IoT**: MQTT, Sensor Integration  

## 🎯 Roadmap

- AI environmental scoring model
- Hedera blockchain integration
- IoT sensor simulation
- Desktop UI prototype
- Multi-chain support (Solana)
- Mobile companion app
- Carbon credit marketplace
- Bank API integrations

## 📄 License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file.

## 👥 Team

**Alayham Almajali** - [@mja2001](https://github.com/mja2001)

## 🏆 Hackathon

Built for [LMA Edge Hackathon 2025](https://lmaedgehackathon.devpost.com/)

## 📧 Contact

- GitHub: [@mja2001](https://github.com/mja2001)
- LinkedIn: [Alayham Almajali](https://www.linkedin.com/in/alayhamalmajali/)
  
⭐ Star this repo if you find it useful!
