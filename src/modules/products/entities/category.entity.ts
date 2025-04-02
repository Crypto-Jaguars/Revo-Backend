import { Entity, Column, PrimaryGeneratedColumn, OneToMany } from 'typeorm';
import { Product } from './product.entity';

@Entity('categories')
export class Category {
  @PrimaryGeneratedColumn('uuid') 
  id: string;

  @Column({ type: 'varchar', length: 255, nullable: false })
  name: string;

  @OneToMany(() => Product, (product) => product.category)
  products: Product[];
}