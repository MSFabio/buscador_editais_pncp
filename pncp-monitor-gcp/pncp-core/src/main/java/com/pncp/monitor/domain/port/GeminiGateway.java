package com.pncp.monitor.domain.port;

import com.pncp.monitor.domain.model.EditalLeve;
import com.pncp.monitor.domain.model.PalavraChave;
import com.pncp.monitor.domain.model.VeredictoGemini;
import java.util.List;

public interface GeminiGateway {
    List<VeredictoGemini> filtrarEditais(
        List<EditalLeve> editais,
        List<PalavraChave> keywords
    );
}
