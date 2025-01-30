import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, TextDataset, DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments
import json
import os

def prepare_training_data(json_file):
    # Load and format training data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Create text file for training
    with open('train.txt', 'w') as f:
        for example in data:
            # Combine prompt and completion with special tokens
            text = example['prompt'] + example['completion'] + '\n\n'
            f.write(text)

def train_model():
    # Initialize tokenizer and model
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')
    
    # Add special tokens if needed
    special_tokens = {
        'pad_token': '<|pad|>',
        'sep_token': '<|sep|>',
        'bos_token': '<|startoftext|>',
        'eos_token': '<|endoftext|>'
    }
    tokenizer.add_special_tokens(special_tokens)
    model.resize_token_embeddings(len(tokenizer))
    
    # Create dataset
    train_dataset = TextDataset(
        tokenizer=tokenizer,
        file_path='train.txt',
        block_size=512
    )
    
    # Create data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Define training arguments
    training_args = TrainingArguments(
        output_dir='./gpt2-soil-advisor',
        overwrite_output_dir=True,
        num_train_epochs=4,
        per_device_train_batch_size=4,
        save_steps=100,
        save_total_limit=2,
        logging_steps=100,
        learning_rate=5e-5,
        warmup_steps=100,
        gradient_accumulation_steps=4
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset
    )
    
    # Train the model
    trainer.train()
    
    # Save the model and tokenizer
    model.save_pretrained('./gpt2-soil-advisor')
    tokenizer.save_pretrained('./gpt2-soil-advisor')

def generate_response(prompt, model_path='./gpt2-soil-advisor'):
    # Load fine-tuned model and tokenizer
    tokenizer = GPT2Tokenizer.from_pretrained(model_path)
    model = GPT2LMHeadModel.from_pretrained(model_path)
    
    # Encode prompt
    inputs = tokenizer.encode(prompt, return_tensors='pt')
    
    # Generate response
    outputs = model.generate(
        inputs,
        max_length=800,
        num_return_sequences=1,
        temperature=0.7,
        top_p=0.9,
        pad_token_id=tokenizer.pad_token_id
    )
    
    # Decode and return response
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

if __name__ == '__main__':
    # Prepare training data
    prepare_training_data('backend/ml/training_data.json')
    
    # Train the model
    train_model()