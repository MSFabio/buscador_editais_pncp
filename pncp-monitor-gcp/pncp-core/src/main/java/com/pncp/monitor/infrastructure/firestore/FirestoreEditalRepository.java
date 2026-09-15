package com.pncp.monitor.infrastructure.firestore;

import com.google.api.core.ApiFuture;
import com.google.cloud.firestore.DocumentSnapshot;
import com.google.cloud.firestore.Firestore;
import com.google.cloud.firestore.FirestoreOptions;
import com.google.cloud.firestore.QueryDocumentSnapshot;
import com.google.cloud.firestore.QuerySnapshot;
import com.pncp.monitor.domain.model.EditalAprovado;
import com.pncp.monitor.domain.port.EditalRepository;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;

@Repository
public class FirestoreEditalRepository implements EditalRepository {

    private static final String COLLECTION_NAME = "editais_aprovados";
    private final Firestore firestore;

    public FirestoreEditalRepository() {
        this.firestore = FirestoreOptions.getDefaultInstance().getService();
    }

    @Override
    public void salvar(EditalAprovado edital) {
        firestore.collection(COLLECTION_NAME).document(edital.id()).set(edital);
    }

    @Override
    public boolean existeById(String id) {
        try {
            ApiFuture<DocumentSnapshot> future = firestore.collection(COLLECTION_NAME).document(id).get();
            DocumentSnapshot document = future.get();
            return document.exists();
        } catch (InterruptedException | ExecutionException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Erro ao verificar edital no Firestore", e);
        }
    }

    @Override
    public List<EditalAprovado> buscarPorPeriodo(Instant inicio, Instant fim) {
        try {
            ApiFuture<QuerySnapshot> future = firestore.collection(COLLECTION_NAME)
                    .whereGreaterThanOrEqualTo("processadoEm", inicio.toString())
                    .whereLessThanOrEqualTo("processadoEm", fim.toString())
                    .get();

            List<EditalAprovado> resultados = new ArrayList<>();
            for (QueryDocumentSnapshot document : future.get().getDocuments()) {
                resultados.add(new EditalAprovado(
                        document.getString("id"),
                        document.getString("objeto"),
                        document.getString("orgao"),
                        document.getString("uf"),
                        document.getString("municipio"),
                        document.getString("modalidade"),
                        new BigDecimal(document.getDouble("valorEstimado").toString()),
                        document.getString("dataAbertura"),
                        document.getString("dataSessao"),
                        document.getString("linkPncp"),
                        document.getString("justificativaGemini"),
                        document.getDouble("confiancaGemini"),
                        document.getString("keywordOrigem"),
                        Instant.parse(document.getString("processadoEm"))
                ));
            }
            return resultados;
        } catch (InterruptedException | ExecutionException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Erro ao buscar editais no Firestore", e);
        }
    }
}
