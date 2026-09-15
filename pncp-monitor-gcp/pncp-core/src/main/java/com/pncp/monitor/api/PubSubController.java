package com.pncp.monitor.api;

import com.pncp.monitor.domain.model.EditalLeve;
import com.pncp.monitor.domain.service.FiltragemService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/pubsub")
public class PubSubController {

    private static final Logger logger = LoggerFactory.getLogger(PubSubController.class);

    private final FiltragemService filtragemService;

    public PubSubController(FiltragemService filtragemService) {
        this.filtragemService = filtragemService;
    }

    @PostMapping("/editais")
    public ResponseEntity<String> receberMensagemPubSub(@RequestBody Map<String, Object> body) {
        logger.info("Recebida mensagem do Pub/Sub");
        // Em um cenário real, extrairia do envelope PubSub (body.message.data) Base64
        return ResponseEntity.ok("Mensagem recebida (Mock Pub/Sub)");
    }

    @PostMapping("/api/trigger/editais")
    public ResponseEntity<String> receberEditaisDireto(@RequestBody List<EditalLeve> editais) {
        logger.info("Recebendo {} editais via API REST (Teste Local)", editais.size());
        try {
            filtragemService.processarEditais(editais);
            return ResponseEntity.ok("Lote processado com sucesso");
        } catch (Exception e) {
            logger.error("Erro ao processar lote local", e);
            return ResponseEntity.internalServerError().body("Erro: " + e.getMessage());
        }
    }
}
