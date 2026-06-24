#!/bin/bash
find src/generated/prisma -name "*.ts" -type f | while read f; do
  sed -i "s|from '\./\([^']*\)'\(.*\)|from './\1.js'\2|g; s|from '\.\./\([^']*\)'\(.*\)|from '../\1.js'\2|g; s|from \"\./\([^\"]*\)\"\(.*\)|from \"./\1.js\"\2|g; s|from \"\.\./\([^\"]*\)\"\(.*\)|from \"../\1.js\"\2|g" "$f"
done
