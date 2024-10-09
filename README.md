## Oiii eu me chamo Dyogo Mondego, Professor de Controle e Automação de Processos, Programação e Tecnologia!
<div align="center">
  <a href="https://github.com/Dyogo199">
  <img height="150em" src="https://github-readme-stats.vercel.app/api?username=Dyogo199&show_icons=true&theme=dracula&include_all_commits=true&count_private=true"/>
  <img height="150em" src="https://github-readme-stats.vercel.app/api/top-langs/?username=Dyogo199&layout=compact&langs_count=7&theme=dracula"/>
</div>
<div style="display: inline_block"><br>
  <img align="center" alt="Dyogo-Js" height="30" width="40" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/javascript/javascript-plain.svg">
  <img align="center" alt="Dyogo-Ts" height="30" width="40" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/typescript/typescript-plain.svg">
  <img align="center" alt="Dyogo-React" height="30" width="40" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/react/react-original.svg">
  <img align="center" alt="Dyogo-HTML" height="30" width="40" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/html5/html5-original.svg">
  <img align="center" alt="Dyogo-CSS" height="30" width="40" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/css3/css3-original.svg">
  <img align="center" alt="Dyogo-Python" height="30" width="40" src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg">
   <img align="center" alt="Dyogo-Angular" height="30" width="40" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/angularjs/angularjs-original.svg">
  <img align="center" alt="Dyogo-Cpp" height="30" width="40" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/cplusplus/cplusplus-original.svg">
  <img align="center" alt="Dyogo-Java" height="30" width="40"  src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/java/java-original.svg">
  
  ##
 
<div> 
  <a href="https://instagram.com/dyogomondego" target="_blank"><img src="https://img.shields.io/badge/-Instagram-%23E4405F?style=for-the-badge&logo=instagram&logoColor=white" target="_blank"></a>
  <a href = "d.m.m.a94@gmail.com"><img src="https://img.shields.io/badge/-Gmail-%23333?style=for-the-badge&logo=gmail&logoColor=white" target="_blank"></a>
  <a href="[https://www.linkedin.com/in/rafaella-ballerini-45875016a](https://www.linkedin.com/in/dyogo-mondego-moraes-86a68658/)" target="_blank"><img src="https://img.shields.io/badge/-LinkedIn-%230077B5?style=for-the-badge&logo=linkedin&logoColor=white" target="_blank"></a> 
 
  <picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Dyogo199/Dyogo199/output/github-contribution-grid-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Dyogo199/Dyogo199/output/github-contribution-grid-snake.svg">
  <img alt="github contribution grid snake animation" src="https://raw.githubusercontent.com/Dyogo199/Dyogo199/output/github-contribution-grid-snake.svg">
</picture>
name: generate animation

on:
  # Executa automaticamente a cada 24 horas
  schedule:
    - cron: "0 0 * * *"  # Executa à meia-noite todos os dias
  
  # Permite rodar o job manualmente
  workflow_dispatch:
  
  # Executa em cada push na branch master
  push:
    branches:
    - master

jobs:
  generate:
    permissions: 
      contents: write
    runs-on: ubuntu-latest
    timeout-minutes: 5
    
    steps:
      # Gera o snake game a partir do gráfico de contribuições do GitHub do usuário e gera uma animação SVG
      - name: generate github-contribution-grid-snake.svg
        uses: Platane/snk/svg-only@v3
        with:
          github_user_name: ${{ github.repository_owner }}
          outputs: |
            dist/github-contribution-grid-snake.svg
            dist/github-contribution-grid-snake-dark.svg?palette=github-dark
          
      # Faz o push do conteúdo gerado para a branch de saída
      - name: push github-contribution-grid-snake.svg to the output branch
        uses: crazy-max/ghaction-github-pages@v3.1.0
        with:
          target_branch: output
          build_dir: dist
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

 
</div>
