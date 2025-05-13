# Principais Dependências

- [customtkinter](https://github.com/TomSchimansky/CustomTkinter)
- [aiohttp](https://docs.aiohttp.org/)
- [sentence-transformers](https://www.sbert.net/)
- [torch](https://pytorch.org/)
- [transformers](https://huggingface.co/docs/transformers/index)
- [reportlab](https://www.reportlab.com/dev/docs/)
- [Ollama](https://ollama.com/)

## Observações

- O sistema prioriza uso de GPU NVIDIA (6GB VRAM) e faz fallback automático para CPU.
- O cache semântico reduz latência para perguntas repetidas.
- O histórico do chat é limitado a 2048 tokens para performance.
- Logs de erro são salvos em `logs/chat_errors_YYYYMMDD.log`.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

**Desenvolvido porJeferson Wohanka**
