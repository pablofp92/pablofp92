---
title: "Modelo de predicción de cáncer de prostata con regresión logística y Support Vector Machines"
output: "prostatemodels"
---

```{r} 
#Chequea e instala paquetes

if (!require("pacman")) install.packages("pacman")
library(pacman)
pacman::p_load(readxl, ggplot2, RColorBrewer, ggbiplot, GGally,dendextend, corrplot, gridExtra, plot3D, dplyr, tidyr, devtools,
               arules, caret, mvnormtest, heplots, mvnormtest, e1071, cluster, pracma, factoextra, NbClust)

# carga manual de paquetes
 library(readxl) #lee xls como dataframe
 library(ggplot2) #paquete de graficos
 library(RColorBrewer) #complemento ggplot
 library(ggbiplot) #para graficar biplot
 library(GGally) #complemento ggplot
 library(dendextend) #complemento para graficar dendrograma
 library(corrplot) #para graficar matrices de correlacion
 library(gridExtra) #complemento ggplot
 library(plot3D) #graficos scatter 3D
 library(dplyr)  #herramienta de manejo de datos
 library(tidyr)  #herramienta de manejo de datos
 library(devtools) # herramientas estadísticas
 library(arules)  # herramientas estadísticas
 library(caret) #herramientas de regresion y clasificacion
 library(mvnormtest) #test normalidad multivariada 
 library(heplots)  # herramientas estadísticas
 library(e1071)  # herramientas estadísticas
 library(cluster) #paquete de clusters
 library(pracma)  # herramientas estadísticas
 library(factoextra) # herramientas estadísticas
 library(NbClust) # tests de cantidad de clusters optimos 
```

 
```{r}
###### PRIMERA PARTE: clasificación supervisada ######
######  Carga de datos ########### Alumno: Pablo Perez
prostata_completo = read_xlsx('prostata.xlsx')
dni=36761117
n=round(0.8* nrow(prostata_completo)) 
set.seed(dni);
cuales= sample(1:nrow(prostata_completo), size=n,  replace=FALSE)
prostata = prostata_completo[cuales,]

```

```{r}
######### preprocesamiento #########

#elimino NAs
prostata = filter(prostata, !is.na(GLEASON))

#tratamiento de outliers
prostata = filter(prostata, AGE>48, GLEASON>0)

#pasa a factor las variables categóricas
prostata$CAPSULE = as.factor(prostata$CAPSULE)
prostata$RACE = as.factor(prostata$RACE)
prostata$DPROS = as.factor(prostata$DPROS)
prostata$DCAPS = as.factor(prostata$DCAPS)
```

```{r}
#### GRAFICOS EXPLORATORIOS ##########

#Histogramas variables continuas 

h1 <- ggplot(prostata, aes(AGE, fill= CAPSULE)) +
    geom_histogram(binwidth = 4) +
    theme_minimal() +
    theme(legend.position = "top") 

h2 <- ggplot(prostata, aes(PSA, fill= CAPSULE)) +
  geom_histogram(binwidth = 4) +
  theme_minimal() +
  theme(legend.position = "none") 


h3 <- ggplot(prostata, aes(GLEASON, fill= CAPSULE)) +
  geom_histogram(binwidth = 1) +
  theme_minimal() +
  theme(legend.position = "none") 

grid.arrange(h1, h2, h3, nrow = 3) 

#Boxplots variables continuas 

b1<- ggplot(prostata, aes(x=CAPSULE, y=AGE, fill=CAPSULE)) +
  geom_boxplot() +
  coord_flip() +
  theme_minimal() +
  theme(axis.title.y = element_blank()) +
    theme(legend.position = "top") 

ylim2 = boxplot.stats(prostata$PSA)$stats[c(1, 5)] #mejoro visualizacion tapando outliers

b2<- ggplot(prostata, aes(x=CAPSULE, y=PSA, fill=CAPSULE)) +
  geom_boxplot() +
  scale_y_continuous(limits = ylim2 * 1.5 ) +
  coord_flip() +
  theme_minimal() +
  theme(axis.title.y = element_blank()) +
  theme(legend.position = "none") 

b3<- ggplot(prostata, aes(x=CAPSULE, y=GLEASON, fill=CAPSULE)) +
  geom_boxplot() +
  coord_flip() +
  theme_minimal() +
  theme(axis.title.y = element_blank()) +
    theme(legend.position = "none") 


grid.arrange(b1, b2, b3, nrow = 3) 


#Gráficos de barra para variables categóricas 

d1 <- ggplot(prostata, aes(RACE, fill=CAPSULE)) +
  geom_bar(position="fill")+
  theme_minimal() +
  scale_x_discrete(breaks = seq(2), labels= c("Blanca", "Negra")) +
  theme(axis.title.y = element_blank()) +
  theme(legend.position = "none") 


d2 <- ggplot(prostata, aes(factor(DCAPS), fill=CAPSULE)) +
  geom_bar(position="fill")+
  theme_minimal() +
  scale_x_discrete(breaks = seq(2), labels= c("Sí", "No")) +
  labs(x= 'DCAPS') +
  theme(axis.title.y = element_blank()) +
  theme(legend.position = "none") 

d3 <- ggplot(prostata, aes(DPROS, fill=CAPSULE)) +
  geom_bar(position="fill")+
  theme_minimal() +
  scale_x_discrete(breaks = seq(4), labels = c('No nódulo', 'Nod. izq.', 'Nod. derecha', 'Nod. ambos lados')) +
  theme(axis.title.y = element_blank()) +
  theme(legend.position = "bottom") 

grid.arrange(d1,d2, d3, layout_matrix = rbind(c(1,2),3))
```


```{r}
####### REGRESION LINEAL SOBRE LA VARIABLE VOL ###########

prostata_vol = filter(prostata, VOL>0)

prostata_no_vol = filter(prostata, VOL==0)
prostata_no_vol$VOL = NA


vol_lg <- lm(VOL ~  AGE + PSA + RACE + GLEASON + DCAPS + DPROS, data = prostata_vol)

prostata_no_vol$VOL <- predict(vol_lg, prostata_no_vol )
prostata_no_vol$ORIGEN  = 'predicho'
prostata_vol$ORIGEN  = 'real'

prostata_vol = rbind(prostata_vol, prostata_no_vol )

prostata_vol= arrange(prostata_vol, VOL)
ggplot(prostata_vol, aes(y= VOL, x=seq(1,length((prostata_vol$VOL))),  colour=ORIGEN)) +
  geom_jitter()

prostata = prostata_vol

```
```{r}
######## TEST DE NORMALIDAD ###### 
#Separa las variables numéricas 
prostata_num = prostata[c(3,7,8,9)] 

mshapiro.test(t(prostata_num)) #rechaza test shapiro wilks multivariado

#qqplots
qq1<- ggplot(prostata) + 
  geom_qq(aes(sample = AGE)) +
  geom_qq_line(aes(sample = AGE))

qq2<-ggplot(prostata) +
  geom_qq(aes(sample = PSA)) +
  geom_qq_line(aes(sample = PSA))

qq3<- ggplot(prostata) +
  geom_qq(aes(sample = GLEASON)) +
  geom_qq_line(aes(sample = GLEASON))

grid.arrange(qq1,qq2,qq3, layout_matrix = rbind(c(1,2),3))

```

```{r}

##### EVALUACION HOMOCEDASTICIDAD #########

M = cor(prostata_num)
corrplot(M,method="number")

#matriz de correlación para ambas clases
capsule0 = filter(prostata, CAPSULE == 0)
capsule1 = filter(prostata, CAPSULE == 1)

corrplot(cor(capsule0[c(3,7,8,9)]),method="circle")
corrplot(cor(capsule1[c(3,7,8,9)] ),method="circle")


# test Levene
leveneTests(prostata_num, prostata$CAPSULE, center = median) #rechaza en PSA

```
```{r}
boxM(prostata_num, prostata$CAPSULE) #rechaza test M Box 

```

```{r}
# Componentes principales 
datos.pc = prcomp(prostata[c(3,7,8,9)] ,scale = T)
prostata$PC = datos.pc$x[,1]
prostata$PC2 = datos.pc$x[,2]

#biplot
ggbiplot(datos.pc, obs.scale=0.5 ,var.scale=1,
         alpha=0.5,groups=factor(prostata$CAPSULE)) +
  scale_color_manual(name="Rotura capsular (CAPSULE)", values=c("indianred2","deepskyblue3"),labels=c("0", "1")) +  
  theme_minimal()+
  theme(legend.direction ="horizontal", legend.position = "top") 


#Jitter plot entre la primera componente principal y DCAPS
ggplot(prostata, aes(x = PC , y= DCAPS , colour =CAPSULE)) +
  geom_jitter()+
  labs(x= 'PC1') +
  theme_minimal() 


```
```{r}
############ REGRESION LOGISTICA ###########

#Separación en  5 k-folds
set.seed(dni);  #shuffle aleatorio
rows <- sample(nrow(prostata))
prostata <- prostata[rows, ]


test_folds = list()
train_folds = list()

for(i in 1:5){
  test_folds[[i]] = slice(prostata, (1+(i*round(nrow(prostata)/5))-round(nrow(prostata)/5)):(i*round(nrow(prostata)/5))) 
  train_folds[[i]] = anti_join(prostata, test_folds[[i]])
}

```


```{r}

# Evaluacion de modelos de regresion logística con distintas combinaciones de variables

variables = c('AGE', 'DCAPS', 'DPROS', 'PSA', 'GLEASON', 'VOL', 'PC', 'PC2')


lista_formulas = vector()
for(k in 1:(length(variables)-1)){              
combinaciones = combn(variables,k)

    for(i in 1:ncol(combinaciones)){
      formula  = paste0('CAPSULE ~ ', paste(combinaciones[,i], collapse = ' + '))       
      lista_formulas =  c(lista_formulas, formula)
    }}



#entrena varios modelos y reporto varias métricas 
modelos = data.frame()
modelos_lg_kfolds = data.frame()

for(v in 1:length(lista_formulas)){
      for(i in 1:5){
        modelo_lg <- glm(as.formula(lista_formulas[v]), data = train_folds[[i]], family=binomial)
        pred_lg_test <- predict(modelo_lg,test_folds[[i]],type = "response")
        clase_lg_test  = ifelse(pred_lg_test>0.4,1,0) 
        
        matrizconfusion = table(test_folds[[i]]$CAPSULE, clase_lg_test, dnn = c("Clase real","Clase predicha"))
        TN = round(matrizconfusion[1])
        FN = round(matrizconfusion[2])
        FP = round(matrizconfusion[3])
        TP = round(matrizconfusion[4])
        precision = TP/(TP + FP)
        recall =  TP/(TP + FN)
        
        modelos[i,'TP'] = TP
        modelos[i,'FN'] = FN
        modelos[i,'TN'] = TN
        modelos[i,'FP'] = FP
        modelos[i,'tasa de error'] = (FN + FP)/nrow(test_folds[[i]])*100
        modelos[i,'Precision'] = precision
        modelos[i,'Recall'] =  recall
        modelos[i,'F1 score'] =  2*((precision*recall)/(precision+recall))
    }
  
    modelos = summarise_all(modelos, .funs=mean)  
    modelos_lg_kfolds =  bind_rows(modelos_lg_kfolds, modelos)
    modelos_lg_kfolds[v,'formula'] = lista_formulas[v]
}
```
```{r}

#Elección del modelo con menor error 

modelos = data.frame()

for(i in 1:5){
  modelo_lg <- glm(CAPSULE ~ DCAPS + DPROS + PSA + GLEASON, data = train_folds[[i]], family=binomial)
  pred_lg_test <- predict(modelo_lg,test_folds[[i]],type = "response")
  clase_lg_test  = ifelse(pred_lg_test>(0.33),1,0) 
  
  matrizconfusion = table(test_folds[[i]]$CAPSULE, clase_lg_test, dnn = c("Clase real","Clase predicha"))
  TN = round(matrizconfusion[1])
  FN = round(matrizconfusion[2])
  FP = round(matrizconfusion[3])
  TP = round(matrizconfusion[4])
  precision = TP/(TP + FP)
  recall =  TP/(TP + FN)
  
  modelos[i,'TP'] = TP
  modelos[i,'FN'] = FN
  modelos[i,'TN'] = TN
  modelos[i,'FP'] = FP
  modelos[i,'tasa de error'] = (FN + FP)/nrow(test_folds[[i]])*100
  modelos[i,'Precision'] = precision
  modelos[i,'Recall'] =  recall
  modelos[i,'F1 score'] =  2*((precision*recall)/(precision+recall))
}
  
modelos = summarise_all(modelos, .funs=mean)  
modelos[1:4] = round(modelos[1:4])

#Matriz de confusion
Real <- factor(c(0, 0, 1, 1))
Prediccion <- factor(c(0, 1, 0, 1))
Freq      <- c(modelos[,'TN'],  modelos[,'FP'], modelos[,'FN'], modelos[,'TP'])
matrizconfusion <- data.frame(Real, Prediccion, Freq)


ggplot(data =  matrizconfusion, mapping = aes(x = Real, y = Prediccion)) +
  geom_tile(aes(fill = Freq), colour = "white") +
  geom_text(aes(label = sprintf("%1.0f", Freq)), vjust = 1, size=6, colour = "white") +
  scale_fill_gradient(low = "dodgerblue1", high = "firebrick2") +
  theme_minimal() + theme(legend.position = "none")
```

```{r}


############ SUPPORT VECTOR MACHINES  ###########


#configura random search
fitControl <- trainControl(method = "cv",
                           number = 10,
                           search = "random")


# Prueba diferentes funciones de Kernel para el SVM
kernels  = c('svmLinear2','svmLinearWeights','svmPoly','svmRadial')

lista_modelos_svm = data.frame()
lista_modelos_svm_kfolds = data.frame()

for(k in 1:length(kernels)){
  for(i in 1:5){
     modelo_svm <- train(CAPSULE ~., data = train_folds[[i]], 
                        method =  kernels[k],
                        tuneLength = 10,
                        trControl = fitControl,
                        metric = "Accuracy")
    
    pred_svm=predict(modelo_svm, test_folds[[i]])
    matrizconfusion = table(test_folds[[i]]$CAPSULE, pred_svm, dnn = c("Clase real", "Clase predicha"))
    error_svm<- mean(test_folds[[i]]$CAPSULE!= pred_svm) * 100
    precision = matrizconfusion[4] /  (matrizconfusion[4]+ matrizconfusion[3])
    recall = matrizconfusion[4] /  (matrizconfusion[4]+ matrizconfusion[2])
    
    lista_modelos_svm[i,'kernel'] =  kernels[k]
    lista_modelos_svm[i,'accuracy'] = modelo_svm$results[2]
    lista_modelos_svm[i,'tasa de error'] = error_svm
    lista_modelos_svm[i,'Precision'] = precision
    lista_modelos_svm[i,'Recall'] =  recall
    lista_modelos_svm[i,'F1 score'] =  2*((precision*recall)/(precision+recall))
    
  }
  lista_modelos_svm_kfolds = bind_rows(lista_modelos_svm_kfolds, lista_modelos_svm)
  lista_modelos_svms_kfolds = lista_modelos_svm %>% group_by(kernel[k]) %>% summarise_all(.funs = mean)


}

lista_modelos_svm_kfolds = lista_modelos_svm_kfolds %>% group_by(kernel) %>% summarise_all(.funs = mean)


# elijo kernel Lineal
# Con este kernel evalúo mejor combinacion de variables

lista_modelos_svm = data.frame()
lista_modelos_svm_kfolds = data.frame()

for(v in 1:length(lista_formulas)){
  for(i in 1:5){
    modelo_svm <- train(as.formula(lista_formulas[v]), data = train_folds[[i]], 
                        method = 'svmLinear2',
                        tuneLength = 10,
                        trControl = fitControl,
                        metric = "Accuracy")
    
    pred_svm=predict(modelo_svm, test_folds[[i]])
    matrizconfusion = table(test_folds[[i]]$CAPSULE, pred_svm, dnn = c("Clase real", "Clase predicha"))
    error_svm<- mean(test_folds[[i]]$CAPSULE!= pred_svm) * 100
    precision = matrizconfusion[4] /  (matrizconfusion[4]+ matrizconfusion[3])
    recall = matrizconfusion[4] /  (matrizconfusion[4]+ matrizconfusion[2])
    
    lista_modelos_svm[i,'formula'] =  lista_formulas[v]
    lista_modelos_svm[i,'tasa de error'] = error_svm
    lista_modelos_svm[i,'Precision'] = precision
    lista_modelos_svm[i,'Recall'] =  recall
    lista_modelos_svm[i,'F1 score'] =  2*((precision*recall)/(precision+recall))
    
  }
  lista_modelos_svm_kfolds = bind_rows(lista_modelos_svm_kfolds, lista_modelos_svm)
  lista_modelos_svm_kfolds = lista_modelos_svm_kfolds %>% group_by(formula) %>% summarise_all(.funs = mean)
  
}


```

```{r}

#Vuelvo a entrenar el modelo buscando más hiperparámetros

lista_modelos_svm = data.frame()
lista_modelos_svm_kfolds = data.frame()


  for(i in 1:5){
    modelo_svm <- train(CAPSULE ~	 DPROS +  DCAPS + GLEASON +PSA , data = train_folds[[i]], 
                        method = 'svmLinear2',
                        tuneLength = 100,
                        trControl = fitControl,
                        metric = "Accuracy")
    
    pred_svm=predict(modelo_svm, test_folds[[i]])
    matrizconfusion = table(test_folds[[i]]$CAPSULE, pred_svm, dnn = c("Clase real", "Clase predicha"))
    TN = round(matrizconfusion[1])
    FN = round(matrizconfusion[2])
    FP = round(matrizconfusion[3])
    TP = round(matrizconfusion[4])
    
    precision = TP/(TP + FP)
    recall =  TP/(TP + FN)
    
    lista_modelos_svm[i,'TP'] = TP
    lista_modelos_svm[i,'FN'] = FN
    lista_modelos_svm[i,'TN'] = TN
    lista_modelos_svm[i,'FP'] = FP
    lista_modelos_svm[i,'tasa de error'] = (FN + FP)/nrow(test_folds[[i]])*100
    lista_modelos_svm[i,'Precision'] = precision
    lista_modelos_svm[i,'Recall'] =  recall
    lista_modelos_svm[i,'F1 score'] =  2*((precision*recall)/(precision+recall))
    
    
  }

lista_modelos_svm_kfolds = lista_modelos_svm %>% summarise_all(.funs = mean)

#Matriz de confusion SVM
Real <- factor(c(0, 0, 1, 1))
Prediccion <- factor(c(0, 1, 0, 1))
Freq      <- c(lista_modelos_svm_kfolds[1,'TN'],  lista_modelos_svm_kfolds[1,'FP'], lista_modelos_svm_kfolds[1,'FN'], lista_modelos_svm_kfolds[1,'TP'])
matrizconfusion_svm <- data.frame(Real,Prediccion, Freq)


ggplot(data =  matrizconfusion_svm, mapping = aes(x = Real, y = Prediccion)) +
  geom_tile(aes(fill = Freq), colour = "white") +
  geom_text(aes(label = sprintf("%1.0f", Freq)), vjust = 1, size=6, colour = "white") +
  scale_fill_gradient(low = "dodgerblue1", high = "firebrick2") +
  theme_minimal() + theme(legend.position = "none")

```

```{r}

#Jitter plot para comparar modelos
prostata$capsule_lg = as.factor(ifelse(predict(modelo_lg, prostata, type='response')>0.33,1,0)) 
prostata$capsule_svm = as.factor(predict(modelo_svm, prostata))
prostata_grafico = dplyr::select(prostata, CAPSULE, PC, PC2)
prostata_grafico$tipo = 'Real' 
prostata_lg = dplyr::select(prostata, capsule_lg, PC, PC2)
prostata_lg$CAPSULE =  prostata_lg$capsule_lg
prostata_lg$tipo = 'Regresion logistica'
prostata_svm = dplyr::select(prostata, capsule_svm, PC, PC2)
prostata_svm$CAPSULE =  prostata_svm$capsule_svm
prostata_svm$tipo = 'SVM'

prostata_grafico = bind_rows(prostata_grafico, prostata_lg, prostata_svm)


ggplot(prostata_grafico, aes(x = PC, y= tipo , colour = CAPSULE)) +
  geom_jitter(height =0.3 , width = 0, alpha = 0.6)+
  labs(x= 'PC 1', y='Modelo') +
  coord_flip() +
  theme_minimal() +
  theme(legend.position = "top") +
  theme(axis.text.y = element_text(angle = 90, vjust=1, hjust=0.5)) +
  theme(axis.text.x=element_text(size=12, face='bold'))

```
