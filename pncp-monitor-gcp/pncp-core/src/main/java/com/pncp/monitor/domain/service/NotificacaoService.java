package com.pncp.monitor.domain.service;

import com.pncp.monitor.domain.model.EditalAprovado;
import com.pncp.monitor.domain.port.EditalRepository;
import com.pncp.monitor.domain.port.NotificacaoGateway;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.List;

@Service
public class NotificacaoService {

    private static final Logger logger = LoggerFactory.getLogger(NotificacaoService.class);

    private final EditalRepository editalRepository;
    private final NotificacaoGateway notificacaoGateway;

    public NotificacaoService(EditalRepository editalRepository, NotificacaoGateway notificacaoGateway) {
        this.editalRepository = editalRepository;
        this.notificacaoGateway = notificacaoGateway;
    }

    /**
     * Envia relatório de editais aprovados nos últimos 7 dias.
     */
    public void enviarRelatorioSemanal(List<String> destinatarios) {
        logger.info("Gerando relatório semanal de editais.");

        Instant fim = Instant.now();
        Instant inicio = fim.minus(7, ChronoUnit.DAYS);

        // Busca editais aprovados nos últimos 7 dias
        List<EditalAprovado> editaisAprovados = editalRepository.buscarPorPeriodo(inicio, fim);

        if (editaisAprovados.isEmpty()) {
            logger.info("Nenhum edital aprovado nos últimos 7 dias. E-mail não será enviado.");
            return;
        }

        String htmlCorpo = construirHtml(editaisAprovados);
        String assunto = "Relatório de Licitações PNCP - " + editaisAprovados.size() + " novos editais";

        // Envia notificação
        notificacaoGateway.enviarRelatorio(htmlCorpo, destinatarios, assunto);
        logger.info("Relatório enviado com sucesso para {} destinatários.", destinatarios.size());
    }

    private String construirHtml(List<EditalAprovado> editais) {
        StringBuilder html = new StringBuilder();
        html.append("<html><body>");
        html.append("<h2>Editais Aprovados Recentes</h2>");
        html.append("<table border='1' cellpadding='5' cellspacing='0'>");
        html.append("<tr>");
        html.append("<th>Órgão</th>");
        html.append("<th>Objeto</th>");
        html.append("<th>Valor Total</th>");
        html.append("<th>Data Abertura</th>");
        html.append("<th>Data Sessão</th>");
        html.append("<th>Link PNCP</th>");
        html.append("</tr>");

        for (EditalAprovado edital : editais) {
            html.append("<tr>");
            html.append("<td>").append(edital.orgao()).append("</td>");
            html.append("<td>").append(edital.objeto()).append("</td>");
            html.append("<td>").append(edital.valorEstimado()).append("</td>");
            html.append("<td>").append(edital.dataAbertura()).append("</td>");
            html.append("<td>").append(edital.dataSessao()).append("</td>");
            html.append("<td><a href='").append(edital.linkPncp()).append("'>Acessar Edital</a></td>");
            html.append("</tr>");
        }

        html.append("</table>");
        html.append("</body></html>");
        return html.toString();
    }
}
