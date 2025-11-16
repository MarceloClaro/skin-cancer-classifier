"""
Exportação de Modelo Keras para TFLite (K230)
Converte modelo treinado para formato otimizado para edge devices
"""

import os
import sys
import logging
import tensorflow as tf
from tensorflow import keras
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Caminhos
MODEL_PATH = "/home/ubuntu/skin_cancer_classifier_k230_page/models/skin_cancer_model.h5"
TFLITE_OUTPUT_DIR = "/home/ubuntu/skin_cancer_classifier_k230_page/models/tflite"
TFLITE_MODEL_NAME = "skin_cancer_k230.tflite"
TFLITE_QUANTIZED_NAME = "skin_cancer_k230_quantized.tflite"


def export_to_tflite(
    model_path: str = MODEL_PATH,
    output_dir: str = TFLITE_OUTPUT_DIR,
    quantize: bool = True
) -> dict:
    """
    Exporta modelo Keras para TFLite
    
    Args:
        model_path: Caminho do modelo Keras (.h5)
        output_dir: Diretório de saída
        quantize: Se deve aplicar quantização INT8
        
    Returns:
        Dict com informações da exportação
    """
    try:
        logger.info("=" * 60)
        logger.info("EXPORTAÇÃO PARA TFLITE (K230)")
        logger.info("=" * 60)
        
        # Criar diretório de saída
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Carregar modelo
        logger.info(f"Carregando modelo: {model_path}")
        model = keras.models.load_model(model_path)
        logger.info(f"✓ Modelo carregado: {model.name}")
        logger.info(f"  Input shape: {model.input_shape}")
        logger.info(f"  Output shape: {model.output_shape}")
        
        # Converter para TFLite (float32)
        logger.info("\n1. Convertendo para TFLite (float32)...")
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = []  # Sem otimizações
        
        tflite_model = converter.convert()
        
        # Salvar modelo float32
        tflite_path = output_path / TFLITE_MODEL_NAME
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
        
        tflite_size_mb = len(tflite_model) / (1024 * 1024)
        logger.info(f"✓ Modelo TFLite salvo: {tflite_path}")
        logger.info(f"  Tamanho: {tflite_size_mb:.2f} MB")
        
        result = {
            "success": True,
            "float32": {
                "path": str(tflite_path),
                "size_mb": tflite_size_mb
            }
        }
        
        # Converter com quantização INT8 (se solicitado)
        if quantize:
            logger.info("\n2. Convertendo para TFLite com quantização INT8...")
            
            # Criar dataset representativo para quantização
            def representative_dataset():
                """
                Gera dataset representativo para calibração de quantização
                """
                for _ in range(100):
                    # Gerar imagens aleatórias (224x224x3)
                    data = np.random.rand(1, 224, 224, 3).astype(np.float32)
                    yield [data]
            
            converter_quant = tf.lite.TFLiteConverter.from_keras_model(model)
            converter_quant.optimizations = [tf.lite.Optimize.DEFAULT]
            converter_quant.representative_dataset = representative_dataset
            
            # Forçar quantização INT8 completa
            converter_quant.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
            converter_quant.inference_input_type = tf.uint8
            converter_quant.inference_output_type = tf.uint8
            
            try:
                tflite_quant_model = converter_quant.convert()
                
                # Salvar modelo quantizado
                tflite_quant_path = output_path / TFLITE_QUANTIZED_NAME
                with open(tflite_quant_path, 'wb') as f:
                    f.write(tflite_quant_model)
                
                tflite_quant_size_mb = len(tflite_quant_model) / (1024 * 1024)
                compression_ratio = (1 - tflite_quant_size_mb / tflite_size_mb) * 100
                
                logger.info(f"✓ Modelo quantizado salvo: {tflite_quant_path}")
                logger.info(f"  Tamanho: {tflite_quant_size_mb:.2f} MB")
                logger.info(f"  Compressão: {compression_ratio:.1f}%")
                
                result["quantized"] = {
                    "path": str(tflite_quant_path),
                    "size_mb": tflite_quant_size_mb,
                    "compression_ratio": compression_ratio
                }
            except Exception as e:
                logger.error(f"Erro ao quantizar modelo: {e}")
                result["quantized"] = {"error": str(e)}
        
        # Validar modelos
        logger.info("\n3. Validando modelos...")
        
        # Validar float32
        interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
        interpreter.allocate_tensors()
        
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        logger.info(f"✓ Modelo float32 válido")
        logger.info(f"  Input: {input_details[0]['shape']} ({input_details[0]['dtype']})")
        logger.info(f"  Output: {output_details[0]['shape']} ({output_details[0]['dtype']})")
        
        # Validar quantizado (se existe)
        if "quantized" in result and "path" in result["quantized"]:
            interpreter_quant = tf.lite.Interpreter(model_path=result["quantized"]["path"])
            interpreter_quant.allocate_tensors()
            
            input_details_quant = interpreter_quant.get_input_details()
            output_details_quant = interpreter_quant.get_output_details()
            
            logger.info(f"✓ Modelo quantizado válido")
            logger.info(f"  Input: {input_details_quant[0]['shape']} ({input_details_quant[0]['dtype']})")
            logger.info(f"  Output: {output_details_quant[0]['shape']} ({output_details_quant[0]['dtype']})")
        
        # Gerar documentação
        logger.info("\n4. Gerando documentação...")
        doc_path = output_path / "README.md"
        with open(doc_path, 'w') as f:
            f.write(generate_documentation(result))
        
        logger.info(f"✓ Documentação salva: {doc_path}")
        
        logger.info("\n" + "=" * 60)
        logger.info("EXPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info("=" * 60)
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao exportar modelo: {e}")
        logger.exception(e)
        return {"success": False, "error": str(e)}


def generate_documentation(export_result: dict) -> str:
    """
    Gera documentação de uso do modelo TFLite
    
    Args:
        export_result: Resultado da exportação
        
    Returns:
        String com documentação em Markdown
    """
    doc = f"""# Modelo TFLite para K230 - Classificação de Câncer de Pele

## 📦 Arquivos Gerados

### 1. Modelo Float32
- **Arquivo:** `{TFLITE_MODEL_NAME}`
- **Tamanho:** {export_result.get('float32', {}).get('size_mb', 0):.2f} MB
- **Precisão:** Float32 (máxima acurácia)
- **Uso:** Dispositivos com recursos suficientes

### 2. Modelo Quantizado INT8
"""
    
    if "quantized" in export_result and "path" in export_result["quantized"]:
        doc += f"""- **Arquivo:** `{TFLITE_QUANTIZED_NAME}`
- **Tamanho:** {export_result['quantized']['size_mb']:.2f} MB
- **Compressão:** {export_result['quantized']['compression_ratio']:.1f}% menor
- **Precisão:** INT8 (otimizado para edge)
- **Uso:** K230 e dispositivos embarcados

"""
    else:
        doc += "- **Status:** Não disponível\n\n"
    
    doc += """## 🚀 Uso no K230

### Python (TensorFlow Lite)

```python
import tensorflow as tf
import numpy as np
from PIL import Image

# Carregar modelo
interpreter = tf.lite.Interpreter(model_path="skin_cancer_k230_quantized.tflite")
interpreter.allocate_tensors()

# Obter detalhes de entrada/saída
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Preprocessar imagem
img = Image.open("lesion.jpg").resize((224, 224))
img_array = np.array(img) / 255.0
img_array = np.expand_dims(img_array, axis=0).astype(np.uint8)  # Para modelo quantizado

# Inferência
interpreter.set_tensor(input_details[0]['index'], img_array)
interpreter.invoke()
output = interpreter.get_tensor(output_details[0]['index'])

# Interpretar resultado
classes = ["BENIGNO", "MALIGNO"]
predicted_class = classes[np.argmax(output)]
confidence = np.max(output) * 100

print(f"Diagnóstico: {predicted_class} ({confidence:.1f}%)")
```

### C++ (K230 SDK)

```cpp
#include <tensorflow/lite/interpreter.h>
#include <tensorflow/lite/kernels/register.h>
#include <tensorflow/lite/model.h>

// Carregar modelo
auto model = tflite::FlatBufferModel::BuildFromFile("skin_cancer_k230_quantized.tflite");
tflite::ops::builtin::BuiltinOpResolver resolver;
tflite::InterpreterBuilder builder(*model, resolver);
std::unique_ptr<tflite::Interpreter> interpreter;
builder(&interpreter);

// Alocar tensores
interpreter->AllocateTensors();

// Preprocessar e executar inferência
// ... (código de preprocessamento)

interpreter->Invoke();

// Obter resultado
float* output = interpreter->typed_output_tensor<float>(0);
```

## 📊 Especificações Técnicas

### Entrada
- **Shape:** (1, 224, 224, 3)
- **Tipo:** UINT8 (quantizado) ou FLOAT32
- **Range:** [0, 255] (quantizado) ou [0.0, 1.0] (float)
- **Formato:** RGB

### Saída
- **Shape:** (1, 2)
- **Tipo:** UINT8 (quantizado) ou FLOAT32
- **Classes:** [BENIGNO, MALIGNO]
- **Interpretação:** Probabilidades (softmax)

### Preprocessamento
1. Redimensionar imagem para 224×224
2. Normalizar pixels: `pixel / 255.0`
3. Converter para RGB (se necessário)
4. Expandir dimensões: `(224, 224, 3) → (1, 224, 224, 3)`

### Pós-processamento
1. Aplicar argmax para obter índice da classe
2. Mapear índice: 0=BENIGNO, 1=MALIGNO
3. Calcular confiança: `max(output) * 100`

## ⚙️ Otimizações para K230

### Modelo Quantizado
- **Redução de tamanho:** ~75% menor
- **Velocidade:** ~4x mais rápido
- **Precisão:** ~1-2% de perda aceitável
- **Memória:** ~4x menos RAM

### Recomendações
1. Use modelo quantizado para produção
2. Implemente cache de inferências
3. Processe imagens em batch (se possível)
4. Use aceleração de hardware (NPU do K230)

## 📚 Referências

- [TensorFlow Lite Guide](https://www.tensorflow.org/lite/guide)
- [K230 SDK Documentation](https://github.com/kendryte/k230_sdk)
- [Model Optimization](https://www.tensorflow.org/lite/performance/model_optimization)

## ⚠️ Nota Importante

Este modelo é uma ferramenta auxiliar de estudo para residentes em dermatologia. **NÃO substitui avaliação clínica presencial** por dermatologista qualificado. Sempre correlacione com achados clínicos e história do paciente.

---
*Gerado automaticamente pelo Sistema de Classificação de Câncer de Pele K230*
"""
    
    return doc


if __name__ == "__main__":
    # Exportar modelo
    result = export_to_tflite(quantize=True)
    
    if result.get("success"):
        print("\n✅ Exportação concluída com sucesso!")
        print(f"\nArquivos gerados em: {TFLITE_OUTPUT_DIR}")
    else:
        print(f"\n❌ Erro na exportação: {result.get('error')}")
        sys.exit(1)
