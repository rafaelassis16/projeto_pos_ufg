class PriorityAdvisor:
    @staticmethod
    def advise(title: str, description: str = "") -> str:
        text = (title + " " + (description or "")).lower()
        if "urgente" in text or "crítico" in text or "imediato" in text:
            return "Alta"
        if "importante" in text or "breve" in text:
            return "Média"
        return "Baixa"
