package com.pncp.monitor.infrastructure.firestore;

import com.google.api.core.ApiFuture;
import com.google.cloud.firestore.Firestore;
import com.google.cloud.firestore.FirestoreOptions;
import com.google.cloud.firestore.QueryDocumentSnapshot;
import com.google.cloud.firestore.QuerySnapshot;
import com.pncp.monitor.domain.model.PalavraChave;
import com.pncp.monitor.domain.port.PalavraChaveRepository;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;

@Repository
public class FirestorePalavraChaveRepository implements PalavraChaveRepository {

    private static final String COLLECTION_NAME = "palavras_chave";
    private final Firestore firestore;

    public FirestorePalavraChaveRepository() {
        this.firestore = FirestoreOptions.getDefaultInstance().getService();
    }

    @Override
    public List<PalavraChave> listarTodas() {
        return buscar("ativa", null);
    }

    @Override
    public List<PalavraChave> listarAtivas() {
        return buscar("ativa", true);
    }

    private List<PalavraChave> buscar(String campo, Boolean valor) {
        try {
            ApiFuture<QuerySnapshot> future;
            if (valor != null) {
                future = firestore.collection(COLLECTION_NAME).whereEqualTo(campo, valor).get();
            } else {
                future = firestore.collection(COLLECTION_NAME).get();
            }

            List<PalavraChave> resultados = new ArrayList<>();
            for (QueryDocumentSnapshot document : future.get().getDocuments()) {
                resultados.add(new PalavraChave(
                        document.getId(),
                        document.getString("termo"),
                        document.getString("contexto"),
                        Boolean.TRUE.equals(document.getBoolean("ativa"))
                ));
            }
            return resultados;
        } catch (InterruptedException | ExecutionException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Erro ao buscar palavras-chave no Firestore", e);
        }
    }

    @Override
    public PalavraChave salvar(PalavraChave keyword) {
        String id = keyword.id() != null ? keyword.id() : firestore.collection(COLLECTION_NAME).document().getId();
        PalavraChave novaKeyword = new PalavraChave(id, keyword.termo(), keyword.contexto(), keyword.ativa());
        firestore.collection(COLLECTION_NAME).document(id).set(novaKeyword);
        return novaKeyword;
    }

    @Override
    public void remover(String id) {
        firestore.collection(COLLECTION_NAME).document(id).delete();
    }
}
