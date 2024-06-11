from tensorflow.keras.applications import DenseNet201
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout

def make_model():
    base_model = DenseNet201(
        weights='imagenet',
        include_top=False,
        input_shape=(224, 224, 3)
    )

    for layer in base_model.layers:
        layer.trainable = False

    # Menambahkan lapisan global average pooling dan lapisan terhubung penuh untuk klasifikasi
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x)  # Menambahkan lapisan terhubung penuh dengan 512 neuron
    x = Dropout(0.2)(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.2)(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.2)(x)
    predictions = Dense(2, activation='softmax')(x)  # Lapisan output dengan fungsi aktivasi softmax

    # Membuat model
    model = Model(inputs=base_model.input, outputs=predictions)
    return model
