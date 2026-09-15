package com.pncp.monitor.domain.port;

import java.util.List;

public interface NotificacaoGateway {
    void enviarRelatorio(String corpoHtml, List<String> destinatarios, String assunto);
}
