package com.pncp.monitor.infrastructure.email;

import com.pncp.monitor.domain.port.NotificacaoGateway;
import com.sendgrid.Method;
import com.sendgrid.Request;
import com.sendgrid.Response;
import com.sendgrid.SendGrid;
import com.sendgrid.helpers.mail.Mail;
import com.sendgrid.helpers.mail.objects.Content;
import com.sendgrid.helpers.mail.objects.Email;
import com.sendgrid.helpers.mail.objects.Personalization;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.List;

@Component
public class SendGridNotificacaoGateway implements NotificacaoGateway {

    private static final Logger logger = LoggerFactory.getLogger(SendGridNotificacaoGateway.class);

    private final String apiKey;
    private final String remetente;

    public SendGridNotificacaoGateway(
            @Value("${notificacao.sendgrid-api-key}") String apiKey,
            @Value("${notificacao.remetente}") String remetente) {
        this.apiKey = apiKey;
        this.remetente = remetente;
    }

    @Override
    public void enviarRelatorio(String corpoHtml, List<String> destinatarios, String assunto) {
        if (apiKey == null || apiKey.isEmpty()) {
            logger.warn("Chave do SendGrid não configurada. E-mail não enviado.");
            return;
        }

        Email from = new Email(remetente);
        Content content = new Content("text/html", corpoHtml);
        Mail mail = new Mail();
        mail.setFrom(from);
        mail.setSubject(assunto);
        mail.addContent(content);

        Personalization personalization = new Personalization();
        for (String dest : destinatarios) {
            personalization.addTo(new Email(dest));
        }
        mail.addPersonalization(personalization);

        SendGrid sg = new SendGrid(apiKey);
        Request request = new Request();
        try {
            request.setMethod(Method.POST);
            request.setEndpoint("mail/send");
            request.setBody(mail.build());
            Response response = sg.api(request);
            logger.info("E-mail enviado via SendGrid com status: {}", response.getStatusCode());
        } catch (IOException ex) {
            logger.error("Erro ao enviar e-mail via SendGrid", ex);
        }
    }
}
