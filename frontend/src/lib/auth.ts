import {hash, compare} from "bcryptjs"

export async function hashPassword(password: string){
  return hash(password, 12)
}

export async function comparePassword(plainPass: string, hashPass: string){
  return compare(plainPass, hashPass)
}