# Trading Bot (Engine)

Modular, async trading engine with plug-in agents.

* **Engine** – Python `asyncio`, Supabase, IBKR  
* **Data** – 1-minute OHLCV + 20-tick buffer  
* **Agents** – Strategies live in `trading_bot/agents/`

See **docs/prd.md** for the full product spec. 
## Development Workflow
See [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) for proper version control practices.

### Quick Setup Scripts
- `./check_status.sh` - Check repository status
- `./setup_runtime_config.sh` - Setup Runtime Config API branch
- `./setup_vm_deployment.sh` - Setup VM Deployment branch
- `./setup_alerting_system.sh` - Setup Alerting System branch
- `./setup_ci_cd_pipeline.sh` - Setup CI/CD Pipeline branch

![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/braedenc/Trading-Bot?utm_source=oss&utm_medium=github&utm_campaign=braedenc%2FTrading-Bot&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)
