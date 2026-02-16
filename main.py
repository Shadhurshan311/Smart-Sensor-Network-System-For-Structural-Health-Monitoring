import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator


image_size = (224, 224)

# Create ImageDataGenerator with grayscale and validation split
data_gen = ImageDataGenerator(
    rescale=1.0 / 255.0,
    validation_split=0.2
)

# Training generator with grayscale
train_gen = data_gen.flow_from_directory(
    r"C:\Users\gkash\Downloads\Pera\FYP\Test IP",
    target_size=image_size,
    color_mode='grayscale',   # <<< Convert to grayscale
    batch_size=32,
    class_mode='binary',
    subset='training',
    shuffle=True
)

# Validation generator with grayscale
val_gen = data_gen.flow_from_directory(
    r"C:\Users\gkash\Downloads\Pera\FYP\Test IP",
    target_size=image_size,
    color_mode='grayscale',   # <<< Convert to grayscale
    batch_size=32,
    class_mode='binary',
    subset='validation',
    shuffle=False
)


from tensorflow.keras import layers, models,regularizers
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.callbacks import ReduceLROnPlateau
from tensorflow.keras.callbacks import ModelCheckpoint

reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.9, patience=2, verbose=1)
early_stop = EarlyStopping(
    monitor='val_loss',     # What to watch (e.g., 'val_loss', 'val_accuracy')
    patience=5,             # Number of epochs to wait for improvement
    restore_best_weights=True  # Revert to best model after stopping
)

checkpoint = ModelCheckpoint(
    filepath='best_model.h5',
    monitor='val_loss',      # or 'val_accuracy'
    save_best_only=True,     # Only save model if metric improves
    mode='min',              # 'min' for loss, 'max' for accuracy
    verbose=1
)


# Define the CNN model
model = models.Sequential([

    layers.Conv2D(16, (3, 3), activation='relu', input_shape=(224, 224, 1)),
    layers.MaxPooling2D(pool_size=(2, 2)),

    layers.Conv2D(16, (3, 3), activation='relu'),
    layers.MaxPooling2D(pool_size=(2, 2)),

    layers.Conv2D(32, (3, 3), activation='relu'),
    layers.MaxPooling2D(pool_size=(2, 2)),

    layers.Conv2D(32, (3, 3), activation='relu'),
    layers.MaxPooling2D(pool_size=(2, 2)),

    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.Conv2D(64, (3, 3), activation='relu'),

    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.Conv2D(128, (3, 3), activation='relu'),

    layers.Flatten(),
    layers.Dense(128, activation='relu',kernel_regularizer=regularizers.L1L2(l1=0.001,l2=0.002),bias_regularizer=regularizers.L2(1e-2), activity_regularizer=regularizers.L2(1e-3)),
    layers.Dropout(0.3),
    layers.Dense(128, activation='relu',kernel_regularizer=regularizers.L1L2(l1=0.001,l2=0.002),bias_regularizer=regularizers.L2(1e-2), activity_regularizer=regularizers.L2(1e-3)),
    layers.Dropout(0.3),
    layers.Dense(1, activation='sigmoid')  # Binary classification


])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

history = model.fit(
    train_gen,
    epochs=50,
    validation_data=val_gen,
    callbacks=[reduce_lr,checkpoint]
)


model.save('best_model.h5')  



# Visualize accuracy and model loss
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.grid()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()