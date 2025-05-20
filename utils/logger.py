class Logger:
    def __init__(self, acesso = "Coder"):
        self.acesso = acesso
    
    def get_color(self):
        match self.gravidade:
            case "erro":
                return "\033[31m"
            case "sucesso":
                return "\033[32m"
            case "aviso":
                return "\033[33m"
            case _:
                return "\033[37m"
    
    def reset(self):
        return "\033[0m"
    
    
    def get_font_style(self):
        match self.custom_font:
            case "italico":
                return "\033[3m"
            case "negrito":
                return "\033[1m"
            case "underline":
                return "\033[4m"
            case _:
                return ""
    
    def format_log(self):
        texto = f"{self.get_font_style()}{self.get_color()}[{self.titulo.upper()}] - {self.mensagem}{self.reset()}"
        return texto
    
    
    def log(self):
        print(self.format_log())
    
    def execute(self, titulo, gravidade, mensagem, custom_font=None):
        self.titulo = titulo
        self.gravidade = gravidade.lower()
        self.mensagem = mensagem
        self.custom_font = custom_font or "Nenhuma"
        self.log()


logger = Logger()