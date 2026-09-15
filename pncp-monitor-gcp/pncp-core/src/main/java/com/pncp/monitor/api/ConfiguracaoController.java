package com.pncp.monitor.api;

import com.pncp.monitor.domain.model.PalavraChave;
import com.pncp.monitor.domain.port.PalavraChaveRepository;
import com.pncp.monitor.domain.service.NotificacaoService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/config")
public class ConfiguracaoController {

    private final PalavraChaveRepository palavraChaveRepository;
    private final NotificacaoService notificacaoService;

    public ConfiguracaoController(PalavraChaveRepository palavraChaveRepository,
                                  NotificacaoService notificacaoService) {
        this.palavraChaveRepository = palavraChaveRepository;
        this.notificacaoService = notificacaoService;
    }

    @GetMapping("/keywords")
    public ResponseEntity<List<PalavraChave>> listarKeywords() {
        return ResponseEntity.ok(palavraChaveRepository.listarTodas());
    }

    @PostMapping("/keywords")
    public ResponseEntity<PalavraChave> criarKeyword(@RequestBody PalavraChave keyword) {
        return ResponseEntity.ok(palavraChaveRepository.salvar(keyword));
    }

    @DeleteMapping("/keywords/{id}")
    public ResponseEntity<Void> deletarKeyword(@PathVariable String id) {
        palavraChaveRepository.remover(id);
        return ResponseEntity.noContent().build();
    }

    // Endpoint de teste manual para notificação
    @PostMapping("/trigger/notificacao")
    public ResponseEntity<String> triggerNotificacao(@RequestParam List<String> emails) {
        notificacaoService.enviarRelatorioSemanal(emails);
        return ResponseEntity.ok("Processo de notificação acionado manualmente.");
    }
}
