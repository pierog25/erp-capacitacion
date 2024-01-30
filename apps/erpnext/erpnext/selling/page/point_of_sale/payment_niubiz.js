class niubizOverskull{
    async generateQRNiubiz(token,amount,date,additionalData,idc){
        const responseQRImg = await fetch('https://apiprod.vnforapps.com/api.qr.manager/v1/qr/ascii', {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                Authorization: token
            },
            body: JSON.stringify({
                param: [
                    {name: 'merchantId', value: '650211627'},//cambiar aqui por el codigo de comercio cuando este en produccion 650211470
                    {name: 'transactionCurrency', value: '604'},
                    {name: 'transactionAmount', value: amount},
                    {name: 'additionalData', value: additionalData},
                    {name: 'idc', value: idc},
                ],
                enabled: true,
                tagType: 'DYNAMIC',
                validityDate: date
            })
        });

        if (!responseQRImg.ok) {
            return {'value':false,'data':{}}
        }
        if(responseQRImg.status != 200) {
            return {'value':false,'data':{}}
        }

        const jsonImg = await responseQRImg.json();
        if(jsonImg.codeResponse==1){
            return {'value':false,'data':jsonImg}
        }

        return {'value':true,'data':jsonImg}
    }

    async generateTokenNiubiz(authEncode){
        const responseToken = await fetch('https://apiprod.vnforapps.com/api.security/v1/security', {
            method: 'GET',
            headers: {
                Accept: 'text/plain',
                Authorization: 'Basic '+authEncode
            }
        });

        if (!responseToken.ok) {
            return {'value':false,'data':{}}
        }
        if(responseToken.status >= 400) {
            return {'value':false,'data':{}}
        }

        const jsonToken = await responseToken.text();
        return {'value':true,'data':jsonToken}
    }
}
